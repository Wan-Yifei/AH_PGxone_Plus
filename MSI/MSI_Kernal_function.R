

# Test kernal density estimation for MSI


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

# 3. Mixture Normal Model

library(mclust)
ModelFit <- function(mark, nsubdis = 2){
  
  colnames(mark) = paste('Mixture Gauss model of', substr(deparse(substitute(mark)),9,nchar(deparse(substitute(mark))) - 1))
  fit = densityMclust(mark[, 1], G = nsubdis, model = 'V')
  print(colnames(mark))
  print(summary(fit,parameters = T)[10:12])
  plot(names(table(mark)), xlab = 'Length', ylab = '', main = paste('Density of ', colnames(mark)))
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

# 4. Variance calculator
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
  var_col = data.frame(c(paste('BAT.25:',var_BAT.25, '\t'), paste('BAT.26:',var_BAT.26, '\t'), paste('NR.21:',var_NR.21, '\t'), paste('NR.24:',var_NR.24, '\t'), paste('NR.27:',var_NR.27, '\t')), stringsAsFactors = F)
  #rownames(var_col) = c('var_BAT.25', 'var_BAT.26', 'var_NR.21', 'var_NR.24', 'var_NR.27')
  return(var_col)
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

################################################################################################
###################################    Running    ##############################################
################################################################################################

setwd('c:/Users/yifei.wan/Desktop')

path_pos <- 'c:/Users/yifei.wan/Desktop/MSI_positive'
path_neg <- 'c:/Users/yifei.wan/Desktop/MSI_negative'

files = list.files(path_pos, pattern = '*.txt')
count_raw <- read.csv(paste(path_pos, files[22], sep = '/'), sep = '\t', header = FALSE, stringsAsFactors = FALSE, row.names = 1)
count_raw <- prestr(count_raw)
prerep(count_raw)


den_27 <- density(BAT.25$MSI_LEN_BAT.25, bw = "nrd0", adjust = 2, kernel = 'gaussian')
#plot(den_27)
plot(prop.table(table(BAT.25)), main = 'Density of Mark', ylab = 'Density')
lines(den_27, # density plot
      lwd = 2, # thickness of line
      col = "chocolate3")

# slope <- (diff(den_27$y)/diff(den_27$x))[findInterval(NR.27$MSI_LEN_NR.27, den_27$x)]
# plot(NR.27$MSI_LEN_NR.27,slope, type = 'b')
# hist(slope)
