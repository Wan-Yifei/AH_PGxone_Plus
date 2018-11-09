# Simulation for sensitivity analysis of MSI detection based in Entropy

###############################################################################
################################ Functions ####################################
###############################################################################

library(entropy)

Info_Entropy <- function(count_raw){
  count_raw[is.na(count_raw)] = 0
  BAT.25 = count_raw['MSI_FREQ_BAT-25', ]
  BAT.26 = count_raw['MSI_FREQ_BAT-26', ]
  NR.21 = count_raw['MSI_FREQ_NR-21', ]
  NR.24 = count_raw['MSI_FREQ_NR-24', ]
  NR.27 = count_raw['MSI_FREQ_NR-27', ]
  
  info_25 = entropy(t(BAT.25), unit = 'log2')
  info_26 = entropy(t(BAT.26), unit = 'log2')
  info_21 = entropy(t(NR.21), unit = 'log2')
  info_24 = entropy(t(NR.24), unit = 'log2')
  info_27 = entropy(t(NR.27), unit = 'log2')
  info_sample = c(info_25, info_26, info_21, info_24, info_27)
  
  return(info_sample)
}


###############################################################################
###############################    Running    #################################
###############################################################################

setwd('c:/Users/yifei.wan/Desktop')

# 1. Negative
path_neg <- 'c:/Users/yifei.wan/Desktop/MSI development/MSI_negative'

files <- list.files(path_neg, pattern = '*.txt')

sink('Information_entropy_neg.txt', append = T)
cat('Sample/Mark', 'BAT.25', 'BAT.26', 'NR.21', 'NR.24', 'NR.27', sep = '\t')
cat('\n')
#sink()
#sink('Information_entropy_neg.txt', append = T)
for (i in 1:length(files)){
  count_raw <- read.csv(paste(path_neg, files[i], sep = '/'), sep = '\t', header = FALSE, stringsAsFactors = FALSE, row.names = 1)
  info_sample <- Info_Entropy(count_raw)
  cat(substr(files[i], 1, nchar(files[i]) - 14), info_sample[1], info_sample[2], info_sample[3], info_sample[4], info_sample[5], sep = '\t')
  cat('\n')
  rm(list = setdiff(ls(), ls.str()))
  gc()
}
sink()


# Positive
path_pos <- 'c:/Users/yifei.wan/Desktop/MSI development/MSI_positive'
files <- list.files(path_pos, pattern = '*.txt')

sink('Information_entropy_pos.txt', append = T)
cat('Sample/Mark', 'BAT.25', 'BAT.26', 'NR.21', 'NR.24', 'NR.27', sep = '\t')
cat('\n')
#sink()
#sink('Information_entropy_neg.txt', append = T)
for (i in 1:length(files)){
  count_raw <- read.csv(paste(path_pos, files[i], sep = '/'), sep = '\t', header = FALSE, stringsAsFactors = FALSE, row.names = 1)
  info_sample <- Info_Entropy(count_raw)
  cat(substr(files[i], 1, nchar(files[i]) - 14), info_sample[1], info_sample[2], info_sample[3], info_sample[4], info_sample[5], sep = '\t')
  cat('\n')
  rm(list = setdiff(ls(), ls.str()))
  gc()
}
sink()
