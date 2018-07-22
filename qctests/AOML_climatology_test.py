# climatology test adpated from Patrick Halsall's 
# ftp://ftp.aoml.noaa.gov/phod/pub/bringas/XBT/AQC/AOML_AQC_2018/codes/qc_checks/clima_checker.py

import sys, numpy
import util.AOMLinterpolation as interp_helper
import util.AOMLnetcdf as read_netcdf

def test(p, parameters):

    qc = numpy.zeros(p.n_levels(), dtype=bool)

    # check for gaps in data
    isTemperature = (p.t().mask==False)
    isDepth = (p.z().mask==False)
    isData = isTemperature & isDepth

    # extract climatology data
    lonlatWithTempsList1, depthColumns1, latLonsList1 = subset_climatology_data(p.longitude(), p.latitude(), "analyzed mean")
    lonlatWithTempsList2, depthColumns2, latLonsList2 = subset_climatology_data(p.longitude(), p.latitude(), "standard deviations")

    for i in range(p.n_levels()):

        if not isData[i]: continue

        interpTemp = interp_helper.temperature_interpolation_process(p.longitude(), p.latitude(), p.z()[i], depthColumns1, latLonsList1, lonlatWithTempsList1, False, "climaInterpTemperature")
        if interpTemp == 99999.99:
            continue
    
        interpTempSD = interp_helper.temperature_interpolation_process(p.longitude(), p.latitude(), p.z()[i], depthColumns2, latLonsList2, lonlatWithTempsList2, False, "climaInterpStandardDev")
        if interpTempSD == 99999.99:
            continue

        qc[i] = climatology_check(p.t()[i], interpTemp, interpTempSD) >= 4

    return qc 

def climatology_check(temperature, interpMNTemp, interpSDTemp):
  """
  temperature: Float for temperature
  interpMNTemp: interpolated temperature from climatology file
  interpSDTemp: interpolated standard deviation from climatology file
  """
  if interpMNTemp == 99999.99 or interpSDTemp == 99999.99:
    return 0

  sigmaFactor = 5.0

  if interpSDTemp <= 0.0:
    return 0
  elif ((abs(temperature-interpMNTemp)/(interpSDTemp*sigmaFactor)) <= 1):
    return 1
  else:
    return 4

def subset_climatology_data(longitude, latitude, statType):
  """
    longitude: float
    latitude: float
    statType: either 'analyzed mean' or 'standard deviations'

    Return list of lists with temperatures that maps one to one with list
      of lists with tuples of latitude and longitude coordinates, list for
      depth measurements, and list of lists with tuples of latitude and
      longitude coordinates that maps one to one with list of lists with
      temperature
    Return an empty list, an empty list, and an empty list if exception
  """
  if statType == "analyzed mean":
    fieldType = "t_an"
    coordinatesScope = 1
  elif statType == "standard deviations":
    fieldType = "t_sd"
    coordinatesScope = 1
  else:
    sys.stderr.write("Cannot process climatology file with a statistical "
                     "field as " + statType + "\n")
    return [], [], []

  filePathName = 'data/woa13_00_025.nc'
  latLonDepthTempList, depthColumns, latLonList, time = (read_netcdf.subset_data(longitude, latitude, filePathName, coordinatesScope, True, fieldType))

  return latLonDepthTempList, depthColumns, latLonList

