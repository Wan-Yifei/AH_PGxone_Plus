#This is a test code for mixture binomial model for MSI

# 1. Input data
setwd('c:/Users/yifei.wan/Desktop')
#count_raw = read.csv('All_counts.txt', sep = '\t', header = FALSE, stringsAsFactors = FALSE)
count_raw = read.csv('Msi_raw_count/1_percent_LoVo_Large-RD_S37_msi_array.txt_counts.txt', sep = '\t', header = FALSE, stringsAsFactors = FALSE)

# 2. Summary
library(ggplot2)
count_raw <- t(count_raw)
colnames(count_raw) <- count_raw[1,]
count_raw <- as.data.frame(count_raw[-1, ])
count_raw <- data.frame(sapply(count_raw, as.character), stringsAsFactors = FALSE)
count_raw <- data.frame(sapply(count_raw, as.integer))
qplot(x = count_raw$MSI_LEN_BAT.26, y = count_raw$MSI_FREQ_BAT.26)

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
  for (i in 1:15){
    row = data.frame(rep(raw_count[i, mark], raw_count[i, mark + 1]))
    count_rep = rbind(count_rep, row)
  }
  colnames(count_rep) = colnames(count_raw)[mark]
  return(count_rep)
}

for(i in 1:10){
  if(i%%2 != 0){
    assign(substr(colnames(count_raw)[i],9, nchar(colnames(count_raw)[i])), freque(count_raw, i))
  }
}

# 5. Mixture Normal Model
library(mclust)
set.seed(121)


# fit25 <- densityMclust(BAT.25[, 1], G =2, model = 'V')
# summary(fit25,parameters=T)
# plot(fit25, what = 'density', xaxt = 'n', yaxt = 'n', xlab = '', main = '')
# par(new = TRUE)
# hist(BAT.25[,1], xlab = 'Length', ylab = '', main = 'Density of BAT.25')
# #plot(fit25, what = 'BIC')

ModelFit <- function(mark, nsubdis = 2){
  fit <- densityMclust(mark[, 1], G = nsubdis, model = 'V')
  print(summary(fit,parameters = T))
  plot(fit, what = 'density', xaxt = 'n', yaxt = 'n', xlab = '', main = '')
  par(new = TRUE)
  hist(mark[,1], xlab = 'Length', ylab = '', main = paste('Density of ', colnames(mark)))
}

ModelFit(BAT.25)
ModelFit(BAT.26, nsubdis = 2)
ModelFit(NR.21)
ModelFit(NR.24, nsubdis = 2)
ModelFit(NR.27)
