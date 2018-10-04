#This is a test code for mixture binomial model for MSI

# 1. Input data
setwd('c:/Users/yifei.wan/Desktop')
#count_raw = read.csv('All_counts.txt', sep = '\t', header = FALSE, stringsAsFactors = FALSE)
#count_raw = read.csv('Msi_raw_count/1_percent_LoVo_Large-RD_S37_msi_array.txt_counts.txt', sep = '\t', header = FALSE, stringsAsFactors = FALSE)
count_raw = read.csv('Msi_raw_count/1_percent_HCT16-Large-RD_S39_msi_array.txt', sep = '\t', header = FALSE, stringsAsFactors = FALSE)

# 2. Prepare structure
prestr <- function(count_raw){
  count_raw <- t(count_raw)
  colnames(count_raw) <- count_raw[1,]
  count_raw <- as.data.frame(count_raw[-1, ])
  count_raw <- data.frame(sapply(count_raw, as.character), stringsAsFactors = FALSE)
  count_raw <- data.frame(sapply(count_raw, as.integer))
  return(count_raw)
}

count_raw <- prestr(count_raw)

# 3. Normalization
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

# 4. Replicate
library(plyr)

freque <- function(raw_count, mark){
  count_rep = data.frame()
  raw_count[is.na(raw_count)] = 0
  #for (i in 1:dim(raw_count)[1]){
  for (i in 1:dim(count_raw[1])){
    row = data.frame(rep(raw_count[i, mark], raw_count[i, mark + 1]))
    count_rep = rbind(count_rep, row)
  }
  colnames(count_rep) = colnames(count_raw)[mark]
  return(count_rep)
}

prerep <- function(count_raw){
  for(i in 1:10){
  if(i%%2 != 0){
    assign(substr(colnames(count_raw)[i],9, nchar(colnames(count_raw)[i])), freque(count_raw, i), envir = .GlobalEnv)
    }
  }
}

prerep(count_raw)

# 5. Mixture Normal Model
library(mclust)


# fit25 <- densityMclust(BAT.25[, 1], G =2, model = 'V')
# summary(fit25,parameters=T)
# plot(fit25, what = 'density', xaxt = 'n', yaxt = 'n', xlab = '', main = '')
# par(new = TRUE)
# hist(BAT.25[,1], xlab = 'Length', ylab = '', main = 'Density of BAT.25')
# #plot(fit25, what = 'BIC')

set.seed(121)
ModelFit <- function(mark, nsubdis = 2){

  fit <- densityMclust(mark[, 1], G = nsubdis, model = 'V')
  print(colnames(mark))
  print(summary(fit,parameters = T))
  barplot(table(mark), xlab = 'Length', ylab = '', main = paste('Density of ', colnames(mark)))  
  par(new = TRUE)
  plot(fit, what = 'density', xaxt = 'n', yaxt = 'n', xlab = '', main = '')
}

MSI_modelfit_main <- function(count_raw){
  set.seed(121)
  count_raw <- prestr(count_raw)
  prerep
  fit_BAT.25 = ModelFit(BAT.25)
  fit_BAT.26 = ModelFit(BAT.26, nsubdis = 2)
  fit_NR.21 = ModelFit(NR.21, nsubdis = 2)
  fit_NR.24 = ModelFit(NR.24, nsubdis = 2)
  fit_NR.27 = ModelFit(NR.27, nsubdis = 2)
}

MSI_modelfit_main(count_raw)
