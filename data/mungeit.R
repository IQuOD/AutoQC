# munges tempRange-raw.csv, a csv of appendix 9.1 in http://data.nodc.noaa.gov/woa/WOD/DOC/wodreadme.pdf
# with all the headers stripped off,
# into temperatureRange.json:
# json rep of the appendix table encoding region names as per http://data.nodc.noaa.gov/woa/WOD/MASKS/range_basin_list.msk

MyData = read.csv(file="tempRange-raw.csv", header=FALSE, sep=",")

nameCodes = (0)

for (i in 2:27){
  nameCodes[i-1] = toString(i)
}

write('{',file="temperatureRange.json",append=FALSE)

write(paste('"levels":[', toString(MyData[1:32, 1]), ', 5500],' ), file='temperatureRange.json', append=TRUE)

for (i in 1:26) {
  write(paste('"', nameCodes[i], '":{', sep=''), file='temperatureRange.json', append=TRUE)
  write(paste('"low":[', toString(MyData[, i*2]), '],' ), file='temperatureRange.json', append=TRUE)
  write(paste('"high":[', toString(MyData[, i*2+1]), ']' ), file='temperatureRange.json', append=TRUE)
  if (i<26) {
    write('},', file='temperatureRange.json', append=TRUE)
  } else {
    write('}', file='temperatureRange.json', append=TRUE)
    write('}', file='temperatureRange.json', append=TRUE)
  }
}

