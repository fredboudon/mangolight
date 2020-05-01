localdir = getSrcDirectory(function(x) {x})
print(localdir)
if (length(localdir) != 0){
  setwd(localdir)
}

input_dir = "./"
eApical = 1
eLateral = 2

data = read.csv(paste(input_dir,"attributeG3.csv",sep=""), header = TRUE)
termdata = data[data$terminal == 1,]
data$light= 4.6*data$light

rel =glm(data$nbleaf ~ data$light * data$diameter  * data$length, family=poisson)
print(rel)
summary(rel)

dataL = data[data$light > 0,]
dataL = dataL[dataL$depth < 20,]
light1 =  dataL$light
depth1 = dataL$depth
loglight = log(light1)
relld = lm(loglight ~ depth1) # + depth2)
print(summary(relld))


library(ggplot2)

plotlightdepth = function(col = 'black', lty="solid", lwd = 3){
  lrange = seq(min(depth1),max(depth1),by=1)
  mtermdata = data.frame(depth1=lrange)
  #print(input)
  prediction = exp(predict(relld, newdata=mtermdata, type="response"))
  #print(prediction)
  d = data.frame(irradiance=prediction, depth=lrange)
  #plot(1,type='n',xlab='GU length', ylab='Number of leaves', xlim = range(length0), ylim = c(0,20)) #range(nbleaf0))
  boxplot(data$light ~ data$depth, xlim=c(0,20), ylab = 'irradiance', xlab= 'depth')
  lines(d, type='l', lwd=lwd, col = 'red')
}

plotlightdepth = function(limit1 = 8, limit2 = 20) {
    dataL = data[data$light > 0,]
    dataL = dataL[dataL$depth <= limit1,]
    light1 =  dataL$light
    depth1 = dataL$depth
    loglight = log(light1)
    relld = lm(loglight ~ depth1) 
    print(summary(relld))
    
    tlrange = seq(min(data$depth), max(data$depth), by=1)
    lrange = seq(0,limit1,by=1)
    mtermdata = data.frame(depth1=lrange)
    prediction = exp(predict(relld, newdata=mtermdata, type="response"))
    
    #d = data.frame(irradiance=prediction, depth=lrange)
    d = data.frame(irradiance=rep(NaN, length(tlrange)), depth=tlrange)
    d[d$depth %in% lrange,]$irradiance = prediction
    label1 =  paste("I =",round(exp(relld$coefficients[1]),2),"exp(",round(relld$coefficients[2],2),"D)")
    
      dataL = data[data$light > 0,]
      dataL = dataL[dataL$depth > limit1,]
      dataL = dataL[dataL$depth < limit2,]
      light1 =  dataL$light
      depth1 = dataL$depth
      relld2 = lm(light1 ~ depth1)
      relld2 = step(relld2)
      print(summary(relld2))
      
      lrange = seq(limit1,limit2,by=1)
      mtermdata = data.frame(depth1=lrange)
      prediction = predict(relld2, newdata=mtermdata, type="response")
      #d2 = data.frame(irradiance=prediction, depth=lrange)
      
      d2 = data.frame(irradiance=rep(NaN, length(tlrange)), depth=tlrange)
      d2[d2$depth %in% lrange,]$irradiance = prediction
      if (is.na(relld2$coefficients[2])) {
        label2 =  paste("I =",round(relld2$coefficients[1],2),"")
      }
      else {
        label2 =  paste("I =",round(relld2$coefficients[2],2),"D +",round(relld2$coefficients[1],2),"")
      }
 
      dataL = data[data$light > 0,]
      dataL = dataL[dataL$depth > limit2,]
      light1 =  dataL$light
      depth1 = dataL$depth
      relld3 = lm(light1 ~ depth1)
      relld3 = step(relld3)
      print(summary(relld3))
      
      lrange = seq(limit2,max(data$depth),by=1)
      mtermdata = data.frame(depth1=lrange)
      prediction = predict(relld3, newdata=mtermdata, type="response")
      #d2 = data.frame(irradiance=prediction, depth=lrange)
      
      d3 = data.frame(irradiance=rep(NaN, length(tlrange)), depth=tlrange)
      d3[d3$depth %in% lrange,]$irradiance = prediction
      if (is.na(relld3$coefficients[2])) {
        label3 =  paste("I =",round(relld3$coefficients[1],2),"")
      }
      else {
        label3 =  paste("I =",round(relld3$coefficients[2],2),"D +",round(relld3$coefficients[1],2),"")
      }
      
       
  pt = ggplot(data, aes(x = factor(depth), y = light, group = depth)) + geom_boxplot() + 
       theme_classic() + theme(legend.position = c(0.5, 0.8), legend.text=element_text(size=6, angle=90)) +
       scale_x_discrete(name = "Growth unit depth (D)") +
       scale_y_continuous(name = expression(paste("Mean irradiance (I) : ",mu,"mol.m-2.s-1"))) +
       coord_cartesian( ylim = c(0, 350), expand = F) + # xlim = c(0, 21.5),
       geom_line(data = d, aes(x=factor(depth), y=irradiance, group=1, colour='black'), size = 2)+
       geom_line(data = d2, aes(x=factor(depth), y=irradiance, group=1, colour="#AAAAAA"), size = 2)+
       geom_line(data = d3, aes(x=factor(depth), y=irradiance, group=1, colour = "#555555"), size = 2)+
       scale_color_manual(values=c("#AAAAAA","#555555","black"), name = "", labels = c(label3,label2,label1) )

  return (pt)
}


plotlightdepth()
break

# plotlightdepth = function(col = 'black', lty="solid", lwd = 3){
#   boxplot(data$light ~ data$depth,  ylim = c(0,100), ylab = 'Mean irradiance (I) : Watt.m-2', xlab= 'Growth unit depth (D)')
#   
#   dataL = data[data$light > 0,]
#   dataL = dataL[dataL$depth < 6,]
#   light1 =  dataL$light
#   depth1 = dataL$depth
#   loglight = log(light1)
#   relld = lm(loglight ~ depth1) # + depth2)
#   print(summary(relld))
#   
#   lrange = seq(0,5,by=1)
#   mtermdata = data.frame(depth1=lrange)
#   prediction = exp(predict(relld, newdata=mtermdata, type="response"))
#   d = data.frame(irradiance=prediction, depth=lrange)
#   lines(d, type='l', lwd=lwd, col = 'red')
#   
#   dataL = data[data$light > 5,]
#   dataL = dataL[dataL$depth < 30,]
#   light1 =  dataL$light
#   depth1 = dataL$depth
#   relld2 = lm(light1 ~ depth1) # + depth2)
#   print(summary(relld2))
#   
#   lrange = seq(5,19,by=1)
#   mtermdata = data.frame(depth1=lrange)
#   prediction = predict(relld2, newdata=mtermdata, type="response")
#   d = data.frame(irradiance=prediction, depth=factor(lrange))
#   lines(d, type='l', lwd=lwd, col = 'blue')
#   
# }

boxplot(data$nbleaf ~ data$depth)

boxplot(data$light ~ data$nbleaf)
boxplot(data$nbleaf~cut(data$light, breaks=20))
#boxplot(data2$nbleaf~cut(log(data2$light), breaks=20))

hist(data$nbleaf)

boxplot(data$nbleaf~cut(data$length, breaks=20))
boxplot(termdata$nbleaf~cut(termdata$length, breaks=20))

nbleaf0 = termdata$nbleaf
length0 =  termdata$length
position0 =  termdata$position
rel = glm(nbleaf0 ~ length0 + position0 , family=poisson)
#rel = lm(nbleaf0 ~ length0 + position0 )
print(summary(rel))

potnbleafpredict2  = function(lgth, position = eApical) {
  mtermdata = data.frame(length0=c(lgth), position0=c(position))
  #print(input)
  value = predict(rel, newdata=mtermdata, type="response")
  return (value)
}

print(potnbleafpredict2(5,eLateral))
print(potnbleafpredict2(seq(min(length0),max(length0),by=0.1),))


plotpotnbleaf = function(col = 'black', lty="solid", lwd = 3){
  lrange = seq(min(length0),max(length0),by=0.1)
  
  boxplot(length0 ~ nbleaf0 , horizontal = T,xlab='Growth unit length', ylab='Number of leaves', xlim = c(1,20.7), ylim = c(0,25))
  
  predictionA = potnbleafpredict2(lrange, eApical)
  dA = data.frame(nbleaf=predictionA, length=lrange)
  lines(dA, type='l', lwd=lwd, col = 'red')
  predictionL = potnbleafpredict2(lrange, eLateral)
  dL = data.frame(nbleaf=predictionL, length=lrange)
  lines(dL, type='l', lwd=lwd, col = 'green')
  legend(0, 21, legend=c("Apical GU", "Lateral GU"), col=c("red", "green"), lwd = lwd)
}

plotpotnbleaf()

potnbleafpredict = function(lgth) { 2.9309 + 0.4095 * lgth}
potnbleafpredict = potnbleafpredict2
lostnbleaf = potnbleafpredict(data$length) - data$nbleaf
boxplot(lostnbleaf~cut(data$light, breaks=20))

potnbleaf = potnbleafpredict(data$length, data$position)
lostnbleaf =  potnbleaf - data$nbleaf
#lostnbleaf[lostnbleaf < 0] = 0
lostratio = lostnbleaf/potnbleaf

lostleafvsdepth = function(maxorder) {
  selection  = (data$depth <= maxorder) 
  selection0 = (data$depth == 0) 
  print(sum(selection))
  lostnbleaf0 = lostnbleaf
  lostnbleaf0[selection0] = 0
  lostnbleafsel = floor(lostnbleaf0)[selection]
  lostnbleafsel[lostnbleafsel < 0 ] = 0
  lostratio = cbind(lostnbleafsel,data$nbleaf[selection])
  depth= data$depth[selection]
  model = glm(lostratio ~ depth, family=binomial)
  return (model)
}


plotlostleafvsdepth = function(maxorder, col = 'red', lty="solid", lwd = 3){
  lld = lostleafvsdepth(maxorder)
  boxplot(lostratio ~ data$depth, xlim=c(0.5,6.4), ylim=c(0,1), ylab = 'Leaf mortality probability', xlab = 'Growth unit depth')
  depths = seq(0,maxorder)
  prediction = predict(lld, newdata=data.frame(depth=depths), type='response')
  print(prediction)
  lines(prediction ~ factor(depths), col = col, lwd=lwd, lty=lty )
}

plotlostleafvsdepth(6)

plotmodel = function(model, order, col = 'black', lty="solid", lwd = 3) {
  l = data$light[data$depth == order]
  light = seq(min(l),max(l),by=10)
  prediction = predict(model, newdata=data.frame(light=light, depth=rep(order,length(light))), type='response')
  lines(prediction ~ light, col = col, lwd=lwd, lty=lty )
}


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
  plot(1,type='n',xlim=c(1,160),ylim=c(0,1),xlab='mean irradiance', ylab='lost leaf ratio')
  colors = gray.colors(maxorder+1,0.0,0.6)
  for (order in 0:maxorder) {
    model = lostleafvslight(order)
    plotmodel(model,order,colors[order+1],order+1, 3)
  }
  legend(2000, 0.8, paste('Depth',0:maxorder), lty=seq(1,maxorder+2), lwd=rep(3,maxorder), col=colors[1:maxorder+1])
  
}

plotallmodels(4)

#
plotallmodels(8)

for (order in 0:4) {
  model = lostleafvslight(order)
  print(summary(model))
}

lostleafvslightndepth = function(maxorder, minlight = 0) {
  selection = (data$depth > 0) & (data$depth <= maxorder) & (data$light >= minlight)
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
  
  plot(1,type='n',xlim=c(1,740),ylim=c(0,1),xlab=expression(paste("Mean irradiance (I) : ",mu,"mol.m-2.s-1")), ylab='Leaf mortality probability')
  colors = gray.colors(maxorder+1,0.0,0.6)
  model = lostleafvslightndepth(maxorder,minlight)
  #model = step(model)
  for (order in 1:maxorder) {
    plotmodel(model,order,colors[order+1],order, 3)
  }
  if (minlight > 0) {
    abline(v=minlight)
  }
  legend(370, 0.8, paste('Depth',1:maxorder), lty=seq(1,maxorder+2), lwd=rep(3,maxorder), col=colors[1:maxorder+1])
  return (model)
}

summary(plotallmodelslightndepth(5,0))

nbleaflight_terminal = function( lty="solid", lwd = 3) {
  dataT = data[data$terminal == 1,]
  print(length(dataT$nbleaf))
  #dataT = data[data$nbleaf > 0,]
  boxplot(dataT$light ~ dataT$nbleaf, xlab = "Number of leaves of terminal growth units (L)",ylab='Mean irradiance (I): Watt.m-2')
  
  meanlight = tapply(dataT$light,dataT$nbleaf,median)
  nbleaf = as.numeric(names(meanlight))
  idata = data.frame(light = meanlight, nbleaf=nbleaf)
  rel0 = lm(meanlight ~ nbleaf, data=idata)
  print(summary(rel0)$r.squared)
  
  rel = lm(log(meanlight) ~ nbleaf, data = idata)
  print(summary(rel)$r.squared)
  nbleaf = seq(0,max(dataT$nbleaf))
  
  prediction0 = predict(rel0, newdata=data.frame(nbleaf=nbleaf), type='response')
  lines(prediction0 ~ factor(nbleaf), col = 'green', lwd=lwd, lty=lty )
  label2 =  paste("L =",round(rel0$coefficients[2],2),"I +",round(rel0$coefficients[1],2),"; r2=",round(summary(rel0)$r.squared,2))
  
  prediction = exp(predict(rel, newdata=data.frame(nbleaf=nbleaf), type='response'))
  lines(prediction ~ factor(nbleaf), col = 'red', lwd=lwd, lty=lty )
  label1 =  paste("L =",round(exp(rel$coefficients[1]),2),"exp(",round(rel$coefficients[2],2),"I) ; r2=",round(summary(rel)$r.squared,2))
  
  
  legend(8.5, 160, legend=c(label1,label2), col=c("red","green"), lwd = lwd)
  return (rel)
}

rel = nbleaflight_terminal()
summary(rel)$r.squared

rootdepth = function(){
  rdepth = data$rootdepth[data$terminal==1]
  hist(rdepth, xlab = 'Distance from trunk base (in number of GU)', ylab = 'Number of terminal growth units', main = '', breaks = max(rdepth))
  mrd = mean(rdepth)
  msd = sd(rdepth)
  rnorm(mrd, msd)
  curve(dnorm(x, mrd, msd)*length(rdepth), min(rdepth), max(rdepth), add=T, col = 'red', lwd = 3)
  legend(6,300,c(paste("N(",round(mrd,2),",",round(msd,2),")",sep="")), col="red", lwd = 3)
}

rootdepth()

nbdaugthers = function(col = 'red', lty="solid", lwd = 3){
  nbdaugthers0 = data$nbdaughters[data$terminal==0]
  depth0 = data$depth[data$terminal==0]
  light0 = data$light[data$terminal==0]
  #plot(data$nbdaughters[data$terminal == 0] ~ data$depth[data$terminal==0])
  boxplot(data$nbdaughters ~ data$depth, ylim = c(0,12), xlab = 'Growth unit depth (D)', ylab = 'Number of daughter growth units')
  
  rel =lm(nbdaugthers0 ~ depth0)
  drange = seq(min(depth0),max(depth0),by=1)
  mtermdata = data.frame(depth0=drange)
  values = predict(rel, newdata=mtermdata, type="response")
  print(values)
  lines(drange, values, col = col, lwd=lwd, lty=lty )
  return (rel)
}

rel = nbdaugthers()
print(summary(rel))


a = c(2,3,2,1,1,1,1,1,1,1,3,3,3,3,3,3,3,3,3,3,1,3,2,3,3,3,2,2,2,3,3,3,3,3,3,3,3,1,2,1,2,3,1,2,2,1,1,3,3,3,3,3,1,1,2,3,3,4,4,4,4,4,3,4,1,1,1,1,1,1,2,3,3,2,2,1,2,1,3,3,3,2,3,3,3,3,3,3,3,3,3,3,3,2,3,3,3,3,3,3,2,1,2,1,1,1,2,3,2,2,1,2,3,3,3,3,3,1,3,1,1,2,3,1,3,3,3,3,3,3,2,1,4,4,4,4,3,3,3,3,3,3,3,3,3,3,3,3,3,2,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,4,4,3,3,4,4,4,1,3,2,2,3,3,3,3,3,2,3,3,3,3,3,3,3,4,4,4,2,4,4,4,3,4,4,1,3,3,3,3,3,2,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,2,1,3,3,3,3,3,2,2,3,3,3,3,3,3,3,3,3,3,3,2,2,3,3,3,3,2,3,3,3,3,2,3,3,3,3,3,3,1,1,1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,2,1,3,2,1,1,1,1,1,1,1,1,3,2,3,1,1,3,3,1,3,3,3,3,1,3,1,3,3,1,3,2,1,2,2,3,2,2,2,3,3,3,3,2,2,3,3,3,3,3,3,3,3,3,3,3,3,3,3,2,3,1,2,1,3,3,3,3,3,3,3,3,3,3,3,3,2,3,3,3,3,3,3,2,3,3,3,3,3,3,3,3,3,3,2,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,2,3,2,1,1,1,2,1,2,2,2,2,1,1,1,3,3,3,3,2,3,2,1,3,3,3,3,3,3,1,1,3,3,3,1,1,1,1,3,3,3,3,3,3,2,2,3,3,3,2,2,3,3,3,3,3,3,3,3,3,3,3,3,3,1,2,2,2,3,3,3,3,3,2,3,1,3,2,1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,2,1,1,2,1,1,2,2,2,2,1,2,4,3,3,3,3,3,1,1,2,1,1,3,3,3,3,3,3,1,1,2,3,3,2,1,1,1,2,1,1,1,3,3,3,1,1,2,2,2,2,3,3,3,3,2,3,3,3,3,3,3,1,2,2,2,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,2,2,1,1,3,1,2,1,1,1,1,3,1,1,3,3,1,2,3,3,3,3,3,3,3,2,1,3,3,2,2,3,3,3,3,2,3,3,3,2,1,3,3,1,2,2,2,3,3,3,3,3,2,3,3,3,3,3,3,1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,2,3,3,3,3,3,3,2,3,3,3,1,3,3,3,3,4,4,4,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,2,3,3,3,3,3,3,3,1,1,1,2,2,2,2,2,2,1,1,1,2,1,1,1,1,1,2,1,2,2,2,2,2,3,3,1,2,1,1,1,1,1,3,3,2,3,3,3,3,3,3,3,3,3,2,3,3,3,3,3,2,3,3,3,3,3,3,3,3,3,3,3,3,2,3,3,3,3,3,3,1,2,1,1,1,1,2,3,3,3,3,3,3,3,3,3,1,1,3,3,1,1,2,1,3,3,3,3,3,3,3,3,3,1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,2,2,3,3,2,1,1,2,1,3,3,3,3,3,3,3,3,3,1,2,2,2,1,1,1,1,2,1,1,1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,2,2,1,1,1,2,1,1,1,2,2,1,1,1,1,1,2,2,1,2,1,1,2,2,2,1,1,1,2,2,1,1,1,1,1,2,2,1,2,1,2,3,3,2,3,3,3,3,3,3,3,3,3,2,2,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,1,2,1,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,2,2,2,1,2,2,2,1,1,1,1,1,1,1,1,1,1,3,3,3,3,3,3,3,3,2,2,1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,2,2,2,2,1,1,1,1,2,2,2,1,2,1,1,2,2,2,2,2,2,2,2,2,2,2,1,2,2,2,2,2,2,2,2,1,1,3,3,3,2,3,3,3,3,2,2,3,3,3,3,3,2,1,2,2,2,2,2,2,2,2,1,2,2,2,2,2,2,2,1,2,2,2,2,2,2,2,1,1,2,2,1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,2,2,2,3,3,3,3,3,1,2,1,2,2,2,1,1,2,2,2,2,2,1,2,2,1,1,2,1,2,1,1,2,1,1,1,1,3,3,1,1,2,2,2,2,1,1,2,1,1,1,1,1,1,1,2,3,1,1,1,1,2,2,2,2,2,2,1,3,3,3,3,3,3,2,1,1,3,3,2,1,3,3,1,1,3,3,3,3,1,2,3,3,3,3,2,2,3,3,2,3,3,3,3,3,3,3,3,3,2,2,2,3,3,2,1,1,2,2,1,1,1,2,2,2,1,1,2,3,3,3,1,1,3,1,3,3,3,3,3,3,3,3,3,1,3,3,3,4,2,2,3,3,3,3,2,3,4,4,3,1,3,3,3,3,3,4,4,4,2,3,3,1,3,1,1,1,1,3,3,3,3,3,2,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,2,1,1,3,3,3,3,3,3,3,3,3,3,3,1,1,1,1,1,1,1,1,1,3,3,3,3,3,3,3,3,3,2,1,1,3,3,3,3,3,3,3,1,1,1,1,1,1,1,1,3,3,3,3,3,2,3,3,3,3,3,3,3,3,3,3,3,3,2,2,2,2,1,1,2,1,2,2,2,2,2,1,2,2,2,2,2,2,2,2,2,1,1,1,2,2,2,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)
b1 = c(1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,2,2,2,2,1,1,1,1,1,2,2,2,3,2,2,2,2,2,2,1,1,2,3,2,2,2,2,2,2,3,3,1,1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,2,1,1,1,1,1,1,1,1,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,1,2,2,2,2,1,1,1,1,2,2,2,2,2,2,2,1,2,2,2,2,2,2,2,2,2,2,2,2,2,1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,2,1,1,1,1,1,1,1,2,1,2,2,1,1,2,2,3,3,3,3,3,3,3,3,3,3,1,1,1,1,2,1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,1,1,1,1,1,1,1,1,1,2,2,2,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,1,2,2,2,2,2,3,3,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,1,2,2,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1)
b2 = c(2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,1,1,1,3,3,3,3,3,3,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,3,3,3,3,3,1,3,3,3,3,1,3,3,3,3,3,3,3,2,2,3,3,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,3,1,3,2,1,1,1,1,1,4,4,4,4,4,4,4,4,4,4,4,4,4,2,2,3,3,3,3,3,3,2,4,4,4,4,4,4,4,4,4,4,4,3,3,3,3,1,3,3,3,3,2,2,2,1,1,1,2,2,1,1,1,2,2,1,1,1,1,1,2,1,1,1,1,1,1,1,1,2,2,2,1,2,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,1,1,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,2,2,1,2,2,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,1,1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,1,1,2,2,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1)
b3=c(1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,3,3,3,3,1,3,3,1,3,3,1,1,1,1,1,1,3,1,1,1,1,1,1,1,2,2,2,3,3,1,1,1,3,3,3,3,3,3,3,3,3,3,3,3,3,2,2,1,3,3,3,3,3,3,3,3,3,3,1,3,3,3,3,1,1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,2,3,3,3,1,3,1,2,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,1,2,1,2,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,1,1,1,1,1,1,1,2,3,3,3,3,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,1,2,3,3,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,3,3,3,3,3,3,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,2,3,3,3,3,3,3,3,3,3,3,1,3,3,3,3,3,3,4,4,3,3,3,3,3,3,3,4,4,1,3,3,3,4,4,3,3,3,3,3,1,1,2,3,3,3,3,3,3,3,1,1,1,1,1,2,2,1,1,1,1,2,2,2,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,1,1,1,1,1,1,1,1,1,2,2,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,2,1,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,2,2,2,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,2,1,1,2,1,3,3,3,3,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,2,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,1,1,1,1,2,2,2,2,2,2,2,2,2,2,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,1,1,1,1,1,1,2,2,2,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,1,1,1,1,1,1,1,3,3,3,3,3,1,2,2,2,2,1,1,3,4,4,4,2,3,3,3,3,3,3,3,3,1,1,2,3,3,3,3,3,1,1,1,1,1,1,2,2,2,2,3,3,3,3,3,3,2,1,1,1,1,1,1,1,2,2,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,3,3,3,3,3,1,1,3,3,3,3,1,3,3,3,3,1,3,3,3,1,1,1,1,3,3,3,3,3,3,3,3,3,3,3,2,2,3,3,3,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,2,2,1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,3,3,3,3,3,3,3,3,3,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,3,3,1,1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1,2,2,2,2,2,1,1,1,2,1,2,2,2,2,2,2,2,2,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,1,2,2,3,3,2,1,1,2,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,1,2,1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,3,3,3,3,3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1)
b4 = c(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)
b = c(b1,b2,b3,b4)

hist(a,breaks =  seq(min(a)-0.5,max(a)+0.5,by=1), xlab="Number of flushes for terminal \n growth units of vegetative cycle 4",ylab="Number of terminal growth units (5 trees)", main="")
hist(b,breaks = seq(min(b)-0.5,max(b)+0.5,by=1), xlab="Number of flushes for terminal \n  growth units of vegetative cycle 5",ylab="Number of terminal growth units (5 trees)", main="")
c = c(a,b)
hist(c,breaks = seq(min(c)-0.5,max(c)+0.5,by=1), xlab="Number of flushes per year",ylab="Number of terminal growth units (5 trees)", main="")
