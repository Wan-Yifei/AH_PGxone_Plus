# Signal inserted simulation for information entropy

###############################################################################
################################ Functions ####################################
###############################################################################


# 1. calculate entropy

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

# 2. Insert signal

MSI_sample_sim <- function(count, signal, site){
  
  ## site - 1: the distance from peak 
  count[is.na(count)] <- 0
  index_ori_max = dim(count)[2]
  peak_ori = which(count == max(count, na.rm = T))
  #print(peak_ori)
  
  ## Prepare the args of signal
  window = dim(signal)[2]
  right_tail = window - which(signal == max(signal, na.rm = T)) 
  
  boundary_right = peak_ori + right_tail - site ## right boundary of area should be processed  
  boundary_left = boundary_right - window + 1 ## left boundary of area should be processed
  
  boundary_right = ifelse(boundary_right > index_ori_max, index_ori_max, boundary_right)
  boundary_left = ifelse(boundary_left < 1, 1, boundary_left)
  #print(boundary_left)
  #print(boundary_right) 
  
  ## normalize signal
  signal = ceiling(signal/rowSums(signal, na.rm = T, dims = 1) * sum(count, na.rm = T) * .03)
  print(signal)
  
  fliter = (window - boundary_right + boundary_left) : window ## which length should be increased
  signal_selected = signal[fliter]
  count_area = count[boundary_left : boundary_right]
  #print(signal_selected)
  #print(count_area)
  #print(1:c(length(fliter)))
  
  ## Insert signal
  count[boundary_left : boundary_right] = count[boundary_left : boundary_right] + signal_selected
  count_insert = count
  
  ## check
  plot(t(count), xlim = c(1, 25), ylim = c(1, max(count, na.rm = T)))
  par(new=TRUE)
  plot(t(signal), xlim = c(1, 25), ylim = c(1, max(count, na.rm = T)), col = 'red')
  #plot(table(count_insert), main = "After insertion")
  #print(table(signal_add))
  #print(table(count[,1]))
  #print(table(count_insert))
  
  #return(count_insert)
  return(count_insert)
}


###############################################################################
###############################    Running    #################################
###############################################################################

setwd('c:/Users/yifei.wan/Desktop')
path_cline <- 'c:/Users/yifei.wan/Desktop/MSI100'
file_cline <- list.files(path_cline, pattern = '*.txt')
count_cline <- read.csv(paste(path_cline, file_cline, sep = '/'), sep = '\t', header = FALSE, stringsAsFactors = FALSE, row.names = 1)
count_cline[is.na(count_cline)] = 0

signal_25 = count_cline['MSI_FREQ_BAT-25', ]
signal_26 = count_cline['MSI_FREQ_BAT-26', ]
signal_21 = count_cline['MSI_FREQ_NR-21', ]
signal_24 = count_cline['MSI_FREQ_NR-24', ]
signal_27 = count_cline['MSI_FREQ_NR-27', ]

which(signal_25 == max(signal_25))
plot(t(signal_25))

path_neg <- 'c:/Users/yifei.wan/Desktop/MSI development/MSI_negative'
files <- list.files(path_neg, pattern = '*.txt')
count_raw <- read.csv(paste(path_neg, files[26], sep = '/'), sep = '\t', header = FALSE, stringsAsFactors = FALSE, row.names = 1)

test25 <- MSI_sample_sim(count_raw['MSI_FREQ_BAT-25', ], signal = signal_25, site = 8)
test26 <- MSI_sample_sim(count_raw['MSI_FREQ_BAT-26', ], signal = signal_26, site = 8)
test21 <- MSI_sample_sim(count_raw['MSI_FREQ_NR-21', ], signal = signal_21, site = 8)
test24 <- MSI_sample_sim(count_raw['MSI_FREQ_NR-24', ], signal = signal_24, site = 8)
test27 <- MSI_sample_sim(count_raw['MSI_FREQ_NR-27', ], signal = signal_27, site = 8)

count = count_raw['MSI_FREQ_BAT-25', ]
signal = signal_25
site =1

test_count <- rbind(test25, test26, test21, test24, test27)

Info_Entropy(test_count)
