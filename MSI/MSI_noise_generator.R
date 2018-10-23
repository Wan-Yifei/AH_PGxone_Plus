# Noise generator

###############################################################
######################### Functions ###########################
###############################################################


Random_signal <- function(scale = 15, skewness = sample(1:scale, 1), intensity = 0.03, count = 10000){
  seeds <- runif(scale, 0, 1)
  signal_pool <- seeds/sum(seeds)
  signal_max <- max(signal_pool)
  signal_tails <- signal_pool[-which(signal_pool == signal_max)]
  group_index <- sample(1:scale - 1, skewness)
  signal_tail_right <- sort(signal_tails[group_index], decreasing = T)
  signal_tail_left <- sort(signal_tails[-group_index])
  signal_pro <- c(signal_tail_left, signal_max, signal_tail_right)
  signal_count <- sample(1:scale, count, replace = T, prob = signal_pro)
  signal_freq <- table(signal_count)
  print(signal_freq)
  signal_count_scaled <- unlist(sapply(1:scale, function(index){rep(index, unname(signal_freq)[index] * intensity)}))
  plot(table(signal_count_scaled))
  return(list(signal_count_scaled))
}

Random_signal()

