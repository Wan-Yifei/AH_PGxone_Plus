# Simulation for sensitivity analysis of MSI detection

########################################################################################
##################################### Functions ########################################
########################################################################################

# 1. Prepare structure

prestr <- function(count_raw){
  count_raw <- data.frame(t(count_raw))
  return(count_raw)
}


# 2. Replicate

## 2.1 Transform frequence to original discrete data
freque <- function(raw_count, mark){
  count_rep = data.frame()
  raw_count[is.na(raw_count)] = 0
  for (i in 1:dim(raw_count)[1]){
    row = data.frame(rep(raw_count[i, mark], raw_count[i, mark + 1]))
    count_rep = rbind(count_rep, row)
  }
  colnames(count_rep) = colnames(count_raw)[mark]
  return(count_rep)
}

## 2.2 Cutoff function
## detect and remove length without count on right side

breakcheck <- function(count_row){
  breakpoints = which(sapply(count_row, function(x)(x+1) %in% count_row) == 0)
  check = ifelse(count_row[breakpoints] > quantile(na.omit(count_row))[3], 1, 0)
  cutpoint = breakpoints[min(which(check == 1))]
  count_row[-c(1:cutpoint)] = NA
  return(count_row)
}

## 2.3 Apply freque to odd columns (length of each mark)
prerep <- function(count_raw){
  for(i in 1:10){
    if(i%%2 != 0){
      count_mark = freque(count_raw, i)
      count_mark[which(count_mark == 0), ] = NA
      assign(substr(colnames(count_raw)[i],9, nchar(colnames(count_raw)[i])), count_mark, envir = .GlobalEnv)
    }
  }
}

# 3. Random signal generator

Random_signal <- function(window = 15, skewness, intensity = 0.03, count = 1e6, rand_seed = runif(1, 1, 1e5), range = 1:window){
  #print(skewness)
  set.seed(rand_seed)
  seeds <- runif(window, 0, 1e7)
  signal_pool <- seeds/sum(seeds)
  signal_max <- max(signal_pool)
  signal_tails <- signal_pool[-which(signal_pool == signal_max)]
  group_index <- sample(2:window - 1, skewness)
  signal_tail_right <- sort(signal_tails[group_index], decreasing = T)
  signal_tail_left <- sort(signal_tails[-group_index])
  signal_pro <- c(signal_tail_left, signal_max, signal_tail_right)
  #print(signal_pro)
  signal_count <- sample(1:window, 1e6, replace = T, prob = signal_pro)
  signal_freq <- table(signal_count)
  #print(sum(signal_freq/1e7*count*0.03))
  signal_count_scaled <- unlist(sapply(1:window, function(index){rep(index, ceiling(unname(signal_freq)[index] / 1e6 * count * intensity))}))
  #plot(table(signal_count_scaled))
  return(signal_count_scaled)
}

# 4. Variance analysis

## 4.1 Calculate the original variance
MSI_var_output <- function(count_raw){
  set.seed(121)
  count_raw = prestr(count_raw)
  prerep(count_raw)
  
  var_BAT.25 = var(BAT.25, na.rm = T)
  var_BAT.26 = var(BAT.26, na.rm = T)
  var_NR.21 = var(NR.21, na.rm = T)
  var_NR.24 = var(NR.24, na.rm = T)
  var_NR.27 = var(NR.27, na.rm = T)
  #var_col = data.frame(c(paste(var_BAT.25, '\t'), paste(var_BAT.26, '\t'), paste(var_NR.21, '\t'), paste(var_NR.24, '\t'), paste(var_NR.27, '\t')), stringsAsFactors = F)
  var_col = data.frame(var_BAT.25, var_BAT.26, var_NR.21, var_NR.24, var_NR.27, stringsAsFactors = F)
  colnames(var_col) = c('BAT.25', 'BAT.26', 'NR.21', 'NR.24', 'NR.27')
  return(var_col)
}

## 4.2 Calculate the total count
MSI_var_count <- function(){
  sum_BAT.25 = dim(na.omit(BAT.25))[1]
  sum_BAT.26 = dim(na.omit(BAT.26))[1]
  sum_NR.21 = dim(na.omit(NR.21))[1]
  sum_NR.24 = dim(na.omit(NR.24))[1]
  sum_NR.27 = dim(na.omit(NR.27))[1]
  #sum_col = data.frame(c(paste(sum_BAT.25, '\t'), paste(sum_BAT.26, '\t'), paste(sum_NR.21, '\t'), paste(sum_NR.24, '\t'), paste(sum_NR.27, '\t')), stringsAsFactors = F)
  sum_col = c(sum_BAT.25, sum_BAT.26, sum_NR.21, sum_NR.24, sum_NR.27)
  return(sum_col)
}

## 4.3 Find Mode
mode <- function(count){
  mode = as.integer(names(table(count))[table(count)==max(table(count))])[1]
  return(mode)
}

# 5. Insert random signal to origianl data
MSI_sample_sim <- function(count, total_count, intensity = 0.03, site, window = 11, right_tail = sample(c(3:7), 1)){
  ## site - 1: the distance from peak 
  #print(right_tail)
  signal = Random_signal(window = window, intensity = intensity, count = total_count, skewness = right_tail)
  signal_count = unname(table(signal))
  #print(signal_count)
  index_ori_max = dim(unique(count))[1]
  peak_ori = which(unique(count) == mode(count))
  #print(peak_ori)
  boundary_right = peak_ori + right_tail - site ## right boundary of area should be processed  
  boundary_left = boundary_right - window + 1 ## left boundary of area should be processed
  range_insert = unique(count)[, 1]
 
  boundary_right = ifelse(boundary_right > index_ori_max, index_ori_max, boundary_right)
  boundary_left = ifelse(boundary_left < 1, 1, boundary_left)
  #print(boundary_left)
  #print(boundary_right) 
  fliter = (window - boundary_right + boundary_left) : window ## which length should be increased
  signal_selected = signal_count[fliter]
  count_area = range_insert[boundary_left : boundary_right]
  #print(signal_selected)
  #print(count_area)
  #print(1:c(length(fliter)))
  
  signal_add = unlist(sapply(c(1:length(fliter)), function(i)rep(count_area[i], signal_selected[i])))
  count_insert = c(count[, 1], signal_add)
  #plot(table(count))
  #plot(table(count_insert), main = "After insertion")
  #print(table(signal_add))
  #print(table(count[,1]))
  #print(table(count_insert))
  
  #return(count_insert)
  return(var(count_insert))
}

# 6. Main function

MSI_batch_sim <- function(count_raw){
  #set.seed(1231)
  count_raw = prestr(count_raw)
  prerep(count_raw)
  
  count_total = MSI_var_count() ## total count for each mark
  sites = c(1:4)
  counts_insert25 = sapply(sites, function(site){MSI_sample_sim(BAT.25, total_count = count_total[1], site = site, right_tail = 5)})
  counts_insert26 = sapply(sites, function(site){MSI_sample_sim(BAT.26, total_count = count_total[2], site = site, right_tail = 5)})
  counts_insert21 = sapply(sites, function(site){MSI_sample_sim(NR.21, total_count = count_total[3], site = site, right_tail = 5)})
  counts_insert24 = sapply(sites, function(site){MSI_sample_sim(NR.24, total_count = count_total[4], site = site, right_tail = 5)})
  counts_insert27 = sapply(sites, function(site){MSI_sample_sim(NR.27, total_count = count_total[5], site = site, right_tail = 5)})
  
  sink('Simulation.txt', append = T)
  cat('Site-3', counts_insert25[1], counts_insert26[1], counts_insert21[1], counts_insert24[1], counts_insert27[1], sep = '\t')
  cat('\n')
  cat('Site-4', counts_insert25[2], counts_insert26[2], counts_insert21[2], counts_insert24[2], counts_insert27[2], sep = '\t')
  cat('\n')
  cat('Site-5', counts_insert25[3], counts_insert26[3], counts_insert21[3], counts_insert24[3], counts_insert27[3], sep = '\t')
  cat('\n')
  cat('Site-6', counts_insert25[4], counts_insert26[4], counts_insert21[4], counts_insert24[4], counts_insert27[4], sep = '\t')
  cat('\n')
  sink()
  gc()
  #return(counts_insert)
}


################################################################################################
######################################    Running    ###########################################
################################################################################################

setwd('c:/Users/yifei.wan/Desktop')
path_neg <- 'c:/Users/yifei.wan/Desktop/MSI development/MSI_negative'

files <- list.files(path_neg, pattern = '*.txt')


# start <- proc.time()
# 
# sink('Simulation.txt', append = T)
# cat('Distance/Mark', 'BAT.25', 'BAT.26', 'NR.21', 'NR.24', 'NR.27', sep = '\t')
# cat('\n')
# sink()
# for (i in 1:length(files)){
#   count_raw <- read.csv(paste(path_neg, files[1], sep = '/'), sep = '\t', header = FALSE, stringsAsFactors = FALSE, row.names = 1)
#   sapply(c(1:1000), function(i){MSI_batch_sim(count_raw = count_raw)})
# }
# 
# print(proc.time() - start)

start <- proc.time()
print(proc.time())
sink('Simulation.txt', append = T)
cat('Distance/Mark', 'BAT.25', 'BAT.26', 'NR.21', 'NR.24', 'NR.27', sep = '\t')
cat('\n')
sink()

count_raw <- read.csv(paste(path_neg, files[1], sep = '/'), sep = '\t', header = FALSE, stringsAsFactors = FALSE, row.names = 1)
sapply(c(1:1000), function(i){MSI_batch_sim(count_raw = count_raw)})

print(proc.time())
print(proc.time() - start)
