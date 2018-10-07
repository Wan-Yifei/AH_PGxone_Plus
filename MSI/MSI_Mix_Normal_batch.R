#This is a test code for mixture binomial model for MSI

# 1. Input data
setwd('c:/Users/yifei.wan/Desktop')
#count_raw = read.csv('All_counts.txt', sep = '\t', header = FALSE, stringsAsFactors = FALSE)
#count_raw = read.csv('Msi_raw_count/1_percent_LoVo_Large-RD_S37_msi_array.txt_counts.txt', sep = '\t', header = FALSE, stringsAsFactors = FALSE)
count_raw <- read.csv('MSI_positive/1_percent_HCT116_Large-RD_S20_msi_array.txt', sep = '\t', header = FALSE, stringsAsFactors = FALSE)

path_pos <- 'c:/Users/yifei.wan/Desktop/MSI_positive'
path_neg <- 'c:/Users/yifei.wan/Desktop/MSI_negative'

input_file <- function(path_way){
  files = list.files(path_way, pattern = '*.txt')
  count_all = sapply(files, function(file)read.csv(paste(path_way, file, sep = '/'), header = F, sep = '\t', stringsAsFactors = F))
  return(count_all)
}

count_all <- input_file(path_pos)

########################################################################################
##################################### Functions ########################################
########################################################################################

# 1. Prepare structure

prestr <- function(count_raw){
  count_raw <- t(count_raw)
  colnames(count_raw) <- count_raw[1,]
  count_raw <- as.data.frame(count_raw[-1, ])
  count_raw <- data.frame(sapply(count_raw, as.character), stringsAsFactors = FALSE)
  count_raw <- data.frame(sapply(count_raw, as.integer))
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



MSI_modelfit_main(count_raw)
