---
title: "Mixture Gauss Model for MSI"
author: "Yifei Wan"
date: "October 5, 2018"
output: html_document
---

```{r functions}
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

prerep <- function(count_raw){
  for(i in 1:10){
    if(i%%2 != 0){
      assign(substr(colnames(count_raw)[i],9, nchar(colnames(count_raw)[i])), freque(count_raw, i), envir = .GlobalEnv)
    }
  }
}

# 3. Mixture Normal Model

ModelFit <- function(mark, nsubdis = 2){
  
  colnames(mark) = paste('Mixture Gauss model of', deparse(substitute(mark)))
  fit = densityMclust(mark[, 1], G = nsubdis, model = 'V')
  print(colnames(mark))
  print(summary(fit,parameters = T)[10:12])
  barplot(table(mark), xlab = 'Length', ylab = '', main = paste('Density of ', colnames(mark)))
  par(new = TRUE)
  plot(fit, what = 'density', xaxt = 'n', yaxt = 'n', xlab = '', main = '')
}

MSI_modelfit_main <- function(count_raw){
  set.seed(121)
  count_raw = prestr(count_raw)
  prerep(count_raw)
  
  library(mclust)
  fit_BAT.25 = ModelFit(BAT.25)
  fit_BAT.26 = ModelFit(BAT.26, nsubdis = 2)
  fit_NR.21 = ModelFit(NR.21, nsubdis = 2)
  fit_NR.24 = ModelFit(NR.24, nsubdis = 2)
  fit_NR.27 = ModelFit(NR.27, nsubdis = 2)
}
```
# The Mixture Gauss Model for MSI detection

This report appears the `mixture Gauss model` for MSI data. The input variable of the model is the count of per length.

We assume the MSI data has two sub-popluations.

## One percent sample

+ Negative Control

```{r AK-large-RD-CNV-R_S9}
setwd('c:/Users/yifei.wan/Desktop')
count_raw <- read.csv('MSI_positive/1_percent_HCT116_Large-RD_S20_msi_array.txt', sep = '\t', header = FALSE, stringsAsFactors = FALSE)
MSI_modelfit_main(count_raw)
```