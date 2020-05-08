localdir = getSrcDirectory(function(x) {x})
print(localdir)
if (length(localdir) != 0){
  setwd(localdir)
}

input_dir = "./"

data = read.csv(paste(input_dir,"attributeG3.csv",sep=""), header = TRUE)

# looking for relation leaf and radius
#library(car)

determine_logrelation = function(y, x, weights = NULL, correction = TRUE) {
  rel = lm(log(y) ~ log(x), weights=weights)
  #sigma = var(log(y), log(x))
  sigma = sum(resid(rel)^2)/df.residual(rel)
  alpha = rel$coefficients[2]
  beta = rel$coefficients[1]
  if (correction)
  { 
    beta = beta + (sigma^2)/2 
  }# (sigma*sigma)/2 }
  
  print(summary(rel))
  print(confint(rel))
  
  
  relfunction = function(x) {
    lny = log(x)*alpha + beta
    return (exp(lny))
  }
  return ( c(relfunction, alpha, beta))
}

determine_relation = function(y, x) {
  rel = lm(y ~ x)

  print(summary(rel))
  print(confint(rel))
  
  
  alpha = rel$coefficients[2]
  beta = rel$coefficients[1]
  
  relfunction = function(x) {
    y = x*alpha + beta
    return (y)
  }
  
  d = y - (alpha*x + b)
  v = sd(d)

  relfunction1 = function(x) {
    y = x*alpha + beta + 2*v
    return (y)
  }

  relfunction2 = function(x) {
    y = x*alpha + beta - 2*v
    return (y)
  }
  
  return ( c(relfunction, alpha, beta, relfunction1, relfunction2))
}


library(latex2exp)

discretize_distribution = function(xvalues, yvalues, nbcuts = 100) {
  nval = cut(xvalues, breaks = nbcuts)
  #nlevels = as.character(levels(nval))
  #nlevels = strsplit(substr(nlevels,2,nchar(nlevels)-1),',')
  #nlevels = (simplify2array(nlevels))
  #nlevels = apply(t(nlevels), 1, function(a) { return ((as.numeric(a[1])+as.numeric(a[2]))/2.) })
  yvalues = as.numeric(tapply(yvalues, nval, mean))
  xvalues = as.numeric(tapply(xvalues, nval, mean)) #nlevels)
  tokeep = !is.na(yvalues)
  yvalues = yvalues[tokeep]
  xvalues = xvalues[tokeep]
  return (list(xvalues, yvalues))
}

id = function(values) { return(values)}

plot_logrelation = function(y, x, func = id, weights = NULL, correction = TRUE, precision = 4, xlab='radius (cm)', ylab = 'Total number of leaves', homogeneous = FALSE){
  
  if (homogeneous){
    data = discretize_distribution(x, y,  nbcuts = 500)
    x = data[[1]]
    y = data[[2]]
  }
  
  relinfo = determine_logrelation(y, x, weights=weights, correction=correction)
  relfunc = relinfo[[1]]
  alpha = relinfo[[2]]
  beta = relinfo[[3]]
  
  maxtla = max(y)
  minx = min(x)
  maxx = max(x)
  radrange = seq(minx,maxx,(maxx-minx)/100)
  plot(func(y) ~ func(x) , xlab = xlab, ylab = ylab)
  lines(func(radrange), func(relfunc(radrange)), col='red', lwd=2)
  #title()
  #legend(func(minx + 0.1*(maxx-minx)), func(maxtla*0.8), TeX(paste('$y = ',format(exp(beta),digits = precision),'x^{',format(alpha,digits = precision),'}$', sep="")), lwd=2, col='red')
  title(paste('alpha = ',format(alpha,digits = precision),', beta = ',format(beta,digits = precision), sep=""))
}

plot_relation = function(y, x, func = id, precision = 4, xlab='radius (cm)', ylab = 'Total number of leaves', homogeneous = FALSE){
  
  if (homogeneous){
    data = discretize_distribution(x, y,  nbcuts = 500)
    x = data[[1]]
    y = data[[2]]
  }
  
  relinfo = determine_relation(y, x)
  relfunc = relinfo[[1]]
  alpha = relinfo[[2]]
  beta = relinfo[[3]]
  
  maxtla = max(y)
  minx = min(x)
  maxx = max(x)
  radrange = seq(minx,maxx,(maxx-minx)/100)
  plot(func(y) ~ func(x) , xlab = xlab, ylab = ylab)
  lines(func(radrange), func(relfunc(radrange)), col='red', lwd=2)
  #title()
  #legend(func(minx + 0.1*(maxx-minx)), func(maxtla*0.8), TeX(paste('$y = ',format(exp(beta),digits = precision),'x^{',format(alpha,digits = precision),'}$', sep="")), lwd=2, col='red')
  title(paste('alpha = ',format(alpha,digits = precision),', beta = ',format(beta,digits = precision), sep=""))
}

data = data[data$pruned==0,]
data0 = data[data$nbtotalleaf>0,]
radius0 = data0$diameter/20
nbtotalleaf = data0$nbtotalleaf

# plot nbleaf vs radius
plot_relation(nbtotalleaf, radius0)

totleafarea = data0$totleafarea/1000000
# plot leaf area vs radius
plot_logrelation(totleafarea, radius0, ylab = 'Total leaf area (m2)')


csa = function(radius){
  return ((radius**2)*pi/10000)
}

csas = csa(radius0)
plot_logrelation(csas, radius0,  xlab='radius (cm)', ylab = 'csa')#,correction = FALSE)

plot_logrelation(nbtotalleaf, csas, xlab='csa (dm2)') #,correction = FALSE)


plot_logrelation(totleafarea, nbtotalleaf, xlab='nb total leaf', ylab = 'Total leaf area (m2)')#, correction = FALSE)


plot_logrelation(totleafarea, csas, xlab='csa (dm2)', ylab = 'Total leaf area (m2)', func = log, correction = T)

plot(nbtotalleaf ~ cut(csas, breaks = 10))




nval = tapply(nbtotalleaf, cut(csas, breaks = 100), mean)



nbtotalleaf2 = discretize_distribution(csas, nbtotalleaf, nbcuts = 500)

plot_logrelation(nbtotalleaf2[[2]], nbtotalleaf2[[1]], correction = FALSE, xlab='csa (dm2)')



totleafarea2 = discretize_distribution(csas, totleafarea, nbcuts = 500)

plot_logrelation(totleafarea2[[2]], totleafarea2[[1]], correction = F, xlab='csa (dm2)', ylab = 'Total leaf area (m2)')


data1 = data
radius1 = data1$diameter/20

plot_logrelation(radius1, data1$nbdescendants,  xlab='nb descendants', ylab = 'radius (cm)')
plot_logrelation(radius1, data1$nbdescendants,  xlab='nb descendants', ylab = 'radius (cm)', h = T)

plot_logrelation(radius1, data1$cumulatedlength/100,  xlab='cumulated length (m)', ylab = 'radius (cm)')
plot_logrelation(radius1, data1$cumulatedlength/100,  xlab='cumulated length (m)', ylab = 'radius (cm)', h = T)


data0 = data[data$nbdescendants == 1,]
data0 = data0[data0$diameter <20,]
plot_relation(data0$diameter/10, data0$length,  xlab='length (cm)', ylab = 'diameter (cm)')
a = 0.0250481
b = 0.2513093
d = data0$diameter/10 - (a*data0$length + b)
d
plot_relation(d, data0$length,  xlab='length (cm)', ylab = 'res (cm)')
sd(d)

plot_relation2 = function(y, x, func = id, precision = 4, xlab='radius (cm)', ylab = 'Total number of leaves', homogeneous = FALSE){
  
  if (homogeneous){
    data = discretize_distribution(x, y,  nbcuts = 500)
    x = data[[1]]
    y = data[[2]]
  }
  
  relinfo = determine_relation(y, x)
  relfunc = relinfo[[1]]
  alpha = relinfo[[2]]
  beta = relinfo[[3]]
  relfunc1 = relinfo[[4]]
  relfunc2 = relinfo[[5]]
  

  
  maxtla = max(y)
  minx = min(x)
  maxx = max(x)
  radrange = seq(minx,maxx,(maxx-minx)/100)
  plot(func(y) ~ func(x) , xlab = xlab, ylab = ylab)
  lines(func(radrange), func(relfunc(radrange)), col='red', lwd=2)
  lines(func(radrange), func(relfunc1(radrange)), col='purple', lwd=1)
  lines(func(radrange), func(relfunc2(radrange)), col='purple', lwd=1)
  #title()
  #legend(func(minx + 0.1*(maxx-minx)), func(maxtla*0.8), TeX(paste('$y = ',format(exp(beta),digits = precision),'x^{',format(alpha,digits = precision),'}$', sep="")), lwd=2, col='red')
  title(paste('alpha = ',format(alpha,digits = precision),', beta = ',format(beta,digits = precision), sep=""))
}

plot_relation2(data0$diameter/10, data0$length,  xlab='length (cm)', ylab = 'diameter (cm)')
