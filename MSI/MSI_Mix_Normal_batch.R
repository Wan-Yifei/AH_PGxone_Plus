#This is a test code for mixture binomial model for MSI

# 1. Input data
setwd('c:/Users/yifei.wan/Desktop')
#count_raw = read.csv('All_counts.txt', sep = '\t', header = FALSE, stringsAsFactors = FALSE)
#count_raw = read.csv('Msi_raw_count/1_percent_LoVo_Large-RD_S37_msi_array.txt_counts.txt', sep = '\t', header = FALSE, stringsAsFactors = FALSE)
#count_raw <- read.csv('MSI_positive/1_percent_HCT116_Large-RD_S20_msi_array.txt', sep = '\t', header = FALSE, stringsAsFactors = FALSE)

path_pos <- 'c:/Users/yifei.wan/Desktop/MSI_positive'
path_neg <- 'c:/Users/yifei.wan/Desktop/MSI_negative'

# input_file <- function(path_way){
#   files = list.files(path_way, pattern = '*.txt')
#   count_all = sapply(files, function(file)read.csv(paste(path_way, file, sep = '/'), header = F, sep = '\t', stringsAsFactors = F))
#   return(count_all)
# }

#count_all <- input_file(path_pos)

########################################################################################
##################################### Functions ########################################
########################################################################################

# 1. Prepare structure

# prestr <- function(count_raw){
#   count_raw <- t(count_raw)
#   colnames(count_raw) <- count_raw[1,]
#   count_raw <- as.data.frame(count_raw[-1, ])
#   count_raw <- data.frame(sapply(count_raw, as.character), stringsAsFactors = FALSE)
#   count_raw <- data.frame(sapply(count_raw, as.integer))
#   return(count_raw)
# }

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

# 3. Mixture Normal Model

library(mclust)
ModelFit <- function(mark, nsubdis = 2){
  
  colnames(mark) = paste('Mixture Gauss model of', substr(deparse(substitute(mark)),9,nchar(deparse(substitute(mark))) - 1))
  fit = densityMclust(mark[, 1], G = nsubdis, model = 'V')
  print(colnames(mark))
  print(summary(fit,parameters = T)[10:12])
  plot(table(mark), xlab = 'Length', ylab = '', main = paste('Density of ', colnames(mark)))
  #barplot(table(mark), xlab = 'Length', ylab = '', main = paste('Density of ', colnames(mark)))
  par(new = TRUE)
  plot(fit, what = 'density', xaxt = 'n', yaxt = 'n', xlab = '', main = '')
}

MSI_modelfit_main <- function(count_raw){
  set.seed(121)
  count_raw = prestr(count_raw)
  count_raw[, seq(1, 9, 2)] = as.data.frame(sapply(count_raw[, seq(1, 9, 2)], breakcheck))
  prerep(count_raw)
  
  fit_BAT.25 = ModelFit(na.omit(BAT.25))
  fit_BAT.26 = ModelFit(na.omit(BAT.26), nsubdis = 2)
  fit_NR.21 = ModelFit(na.omit(NR.21), nsubdis = 2)
  fit_NR.24 = ModelFit(na.omit(NR.24), nsubdis = 2)
  fit_NR.27 = ModelFit(na.omit(NR.27), nsubdis = 2)
}

# 4. Normalization
# Normalize <- function(count_raw){
#   tmp <- count_raw
#   index <- c(2, 4, 6, 8, 10)
#   total_counts <- colSums(count_raw[, index], na.rm = T)
#   for (i in 1:10){
#     if(i%%2 == 0){
#       tmp[, i] <- count_raw[, i]/total_counts[i-1]
#     }
#   }
#   count_normalized <- tmp
#   return(count_normalized)
#   rm(tmp)
#   gc()
# }
# 
# count_normalized <- Normalize(count_raw)

# 5. Variance calculator
MSI_var_output <- function(count_raw){
  set.seed(121)
  count_raw = prestr(count_raw)
  #count_raw[, seq(1, 9, 2)] = as.data.frame(sapply(count_raw[, seq(1, 9, 2)], breakcheck))
  prerep(count_raw)
  
  var_BAT.25 = var(BAT.25, na.rm = T)
  var_BAT.26 = var(BAT.26, na.rm = T)
  var_NR.21 = var(NR.21, na.rm = T)
  var_NR.24 = var(NR.24, na.rm = T)
  var_NR.27 = var(NR.27, na.rm = T)
  var_col = data.frame(c(paste(var_BAT.25, '\t'), paste(var_BAT.26, '\t'), paste(var_NR.21, '\t'), paste(var_NR.24, '\t'), paste(var_NR.27, '\t')), stringsAsFactors = F)
  #rownames(var_col) = c('var_BAT.25', 'var_BAT.26', 'var_NR.21', 'var_NR.24', 'var_NR.27')
  return(var_col)
}

MSI_count_output <- function(count_raw){
  set.seed(121)
  count_raw = prestr(count_raw)
  #count_raw[, seq(1, 9, 2)] = as.data.frame(sapply(count_raw[, seq(1, 9, 2)], breakcheck))
  prerep(count_raw)
  
  sum_BAT.25 = dim(na.omit(BAT.25))[1]
  sum_BAT.26 = dim(na.omit(BAT.26))[1]
  sum_NR.21 = dim(na.omit(NR.21))[1]
  sum_NR.24 = dim(na.omit(NR.24))[1]
  sum_NR.27 = dim(na.omit(NR.27))[1]
  sum_col = data.frame(c(paste(sum_BAT.25, '\t'), paste(sum_BAT.26, '\t'), paste(sum_NR.21, '\t'), paste(sum_NR.24, '\t'), paste(sum_NR.27, '\t')), stringsAsFactors = F)
  #rownames(var_col) = c('var_BAT.25', 'var_BAT.26', 'var_NR.21', 'var_NR.24', 'var_NR.27')
  return(sum_col)
}


MSI_var <- function(count_raw){
  set.seed(121)
  count_raw = prestr(count_raw)
  #count_raw[, seq(1, 9, 2)] = as.data.frame(sapply(count_raw[, seq(1, 9, 2)], breakcheck))
  prerep(count_raw)
  
  var_BAT.25 = var(BAT.25, na.rm = T)
  var_BAT.26 = var(BAT.26, na.rm = T)
  var_NR.21 = var(NR.21, na.rm = T)
  var_NR.24 = var(NR.24, na.rm = T)
  var_NR.27 = var(NR.27, na.rm = T)
  var_col = data.frame(var_BAT.25, var_BAT.26, var_NR.21, var_NR.24, var_NR.27)
  colnames(var_col) = c('BAT.25', 'BAT.26', 'NR.21', 'NR.24', 'NR.27')
  return(var_col)
}

MSI_sd <- function(count_raw){
  set.seed(121)
  count_raw = prestr(count_raw)
  #count_raw[, seq(1, 9, 2)] = as.data.frame(sapply(count_raw[, seq(1, 9, 2)], breakcheck))
  prerep(count_raw)
  
  var_BAT.25 = sd(BAT.25, na.rm = T)
  var_BAT.26 = sd(BAT.26, na.rm = T)
  var_NR.21 = sd(NR.21, na.rm = T)
  var_NR.24 = sd(NR.24, na.rm = T)
  var_NR.27 = sd(NR.27, na.rm = T)
  var_col = data.frame(var_BAT.25, var_BAT.26, var_NR.21, var_NR.24, var_NR.27)
  colnames(var_col) = c('BAT.25', 'BAT.26', 'NR.21', 'NR.24', 'NR.27')
  return(var_col)
}
################################################################################################
###################################    Running    ##############################################
################################################################################################



# Calculate and output variance
files = list.files(path_neg, pattern = '*.txt')
sink("Variance_neg.txt")

for (i in 1:length(files)){
  count_raw <- read.csv(paste(path_neg, files[i], sep = '/'), sep = '\t', header = FALSE, stringsAsFactors = FALSE, row.names = 1)
  #cat('\n\n')
  #print('#################################################################################')
  #print(paste('Sample: ', gsub(x = files[i], pattern = '.txt', replacement = '') ))
  cat('\n')
  cat(c(paste(files[i], '\t'), MSI_var_output(count_raw)[[1]]))
}

sink()

## Chinese sample
path_CHN <- 'c:/Users/yifei.wan/Desktop/MSI development/MSI_CHN'
files <- list.files(path_CHN, pattern = '*.txt')
sink("Variance_CHN.txt")
cat(paste('Sample', 'BAT.25_var', 'BAT.26_var', 'NR.21_var', 'NR.24_var', 'NR.27_var', 'BAT.25_sum', 'BAT.26_sum', 'NR.21_sum', 'NR.24_sum', 'NR.27_sum', sep = '\t'))
for (i in 1:length(files)){
  count_raw <- read.csv(paste(path_CHN, files[i], sep = '/'), sep = '\t', header = FALSE, stringsAsFactors = FALSE, row.names = 1)
  cat('\n')
  name <- unlist(strsplit(files[i], '_'))[1]
  cat(c(paste(name, '\t'), MSI_var_output(count_raw)[[1]], MSI_count_output(count_raw)[[1]]))
}

sink()

# Summary of variance

## negative control

files = list.files(path_neg, pattern = '*.txt')
var_neg <- data.frame()
for (i in 1:length(files)){
  count_raw <- read.csv(paste(path_neg, files[i], sep = '/'), sep = '\t', header = FALSE, stringsAsFactors = FALSE, row.names = 1)
  tmp = MSI_var(count_raw)
  rownames(tmp) = files[i]
  var_neg = rbind(var_neg, tmp)
}


boxplot(var_neg)


sapply(var_neg, var)
sapply(var_neg, sd)
sapply(var_neg, mean)

## positive control

files = list.files(path_pos, pattern = '*.txt')
var_pos <- data.frame()
for (i in 1:length(files)){
  count_raw <- read.csv(paste(path_pos, files[i], sep = '/'), sep = '\t', header = FALSE, stringsAsFactors = FALSE, row.names = 1)
  tmp = MSI_var(count_raw)
  rownames(tmp) = files[i]
  var_pos = rbind(var_neg, tmp)
}

boxplot(var_pos)


