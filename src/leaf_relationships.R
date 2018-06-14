localdir = getSrcDirectory(function(x) {x})
print(localdir)
if (length(localdir) != 0){
  setwd(localdir)
}

input_dir = "./"

data = read.csv(paste(input_dir,"attributeG3.csv",sep=""), header = TRUE)

rel =glm(data$nbleaf ~ data$light * data$radius  * data$length, family=poisson)
print(rel)
summary(rel)

boxplot(data$light ~ data$nbleaf)
boxplot(data$nbleaf~cut(data$light, breaks=20))
#boxplot(data2$nbleaf~cut(log(data2$light), breaks=20))

hist(data$nbleaf)

boxplot(data$radius~data$nbleaf)

potnbleafpredict = function(lgth) { 2.9309 + 0.4095 * lgth}
lostnbleaf = potnbleafpredict(data$length) - data$nbleaf
boxplot(lostnbleaf~cut(data$light, breaks=20))

potnbleaf = potnbleafpredict(data$length)
lostnbleaf =  potnbleaf - data$nbleaf
#lostnbleaf[lostnbleaf < 0] = 0
lostratio = lostnbleaf/potnbleaf

#boxplot(lostnbleaf ~ data$depth)
boxplot(lostratio ~ data$depth)
#boxplot(potnbleaf ~ data$depth)

par(mfrow=c(2,3))
boxplot(lostratio[data$depth == 0]~cut(data$light[data$depth == 0], breaks=10))
boxplot(lostratio[data$depth == 1]~cut(data$light[data$depth == 1], breaks=10))
boxplot(lostratio[data$depth == 2]~cut(data$light[data$depth == 2], breaks=10))
boxplot(lostratio[data$depth == 3]~cut(data$light[data$depth == 3], breaks=10))
boxplot(lostratio[data$depth == 4]~cut(data$light[data$depth == 4], breaks=10))
boxplot(lostratio[data$depth == 5]~cut(data$light[data$depth == 5], breaks=10))

par(mfrow=c(1,1))

lostleafvslight = function(order) {
  selection = data$depth == order
  lostnbleafsel = round(lostnbleaf)[selection]
  lostnbleafsel[lostnbleafsel < 0 ] = 0
  lostratio = cbind(lostnbleafsel,data$nbleaf[selection])
  light = data$light[selection]
  model = glm(lostratio ~ light, family=binomial)
  return (model)
}

plotmodel = function(model, order, col = 'black', lty="solid", lwd = 3) {
  l = data$light[data$depth == order]
  light = seq(min(l),max(l),by=10)
  prediction = predict(model, newdata=data.frame(light=light, depth=rep(order,length(light))), type='response')
  lines(prediction ~ light, col = col, lwd=lwd, lty=lty )
}

plotallmodels = function(maxorder) {
  plot(1,type='n',xlim=c(1,4000),ylim=c(0,1),xlab='irradiance', ylab='lost leaf ratio')
  colors = gray.colors(maxorder+1,0.0,0.6)
  for (order in 0:maxorder) {
    model = lostleafvslight(order)
    plotmodel(model,order,colors[order+1],order+1, 3)
  }
  legend(3000, 0.8, paste('depth',0:maxorder), lty=seq(1,maxorder+2), lwd=rep(3,maxorder), col=colors[1:maxorder+1])
  
}

plotallmodels(4)

#plotallmodels(8)

for (order in 0:4) {
  model = lostleafvslight(order)
  print(summary(model))
}

lostleafvslightndepth = function(maxorder, minlight = 0) {
  selection = (data$depth <= maxorder) & (data$light >= minlight)
  print(sum(selection))
  lostnbleafsel = round(lostnbleaf)[selection]
  lostnbleafsel[lostnbleafsel < 0 ] = 0
  lostratio = cbind(lostnbleafsel,data$nbleaf[selection])
  light = data$light[selection]
  depth= data$depth[selection]
  model = glm(lostratio ~ light * depth, family=binomial)
  return (model)
}

plotallmodelslightndepth = function(maxorder, minlight = 0) {
  plot(1,type='n',xlim=c(1,4000),ylim=c(0,1),xlab='irradiance', ylab='lost leaf ratio')
  colors = gray.colors(maxorder+1,0.0,0.6)
  model = lostleafvslightndepth(maxorder,minlight)
  #model = step(model)
  for (order in 0:maxorder) {
    plotmodel(model,order,colors[order+1],order+1, 3)
  }
  if (minlight > 0) {
    abline(v=minlight)
  }
  legend(3000, 0.8, paste('depth',0:maxorder), lty=seq(1,maxorder+2), lwd=rep(3,maxorder), col=colors[1:maxorder+1])
  return (model)
}

summary(plotallmodelslightndepth(4,0))
