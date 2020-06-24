#!/usr/bin/env python
#
# Author: Patrick Halsall

import sys
from . import AOMLinterpolation as interp_helper
import numpy as np
from netCDF4 import Dataset

def subset_data(x, y, netcdFile, cScope, clima, fieldType):
  """
    Function is expecting 6 arguments:
      Float for longitude
      Float for latitude
      String for path and filename to configuration file
      Float for range of coordinates to gather
      Boolean for evaluating if climatology data or not
      String for type of climatology data

    Process:
      Open netCDF as read only
      Get timestamp, depth measurements, longitudes and latitudes
      Get ranges of index numbers from latitude and longitude lists of
        points near coordinates to limit size
      Call functions to organize longitude and latitude in list of lists and
        map its index numbers with a list of temperatures index numbers

    Return list of lists of latitude and longitude points, list for depth
      measurements, list of lists with temperatures, timestamp in netCDF
    Return empty list, an empty list, an empty list, -1 if exception
  """

  nf = Dataset(netcdFile, "r")
    
  if clima:
    time = nf.variables["time"][0]
    deps = nf.variables["depth"][:]
    lats = nf.variables["lat"][:]
    lons = nf.variables["lon"][:]
  else:
    time = nf.variables["Time"][0]
    deps = nf.variables["zt_k"][:]
    lats = nf.variables["yt_j"][:]
    lons = nf.variables["xt_i"][:]
  temperatureType = fieldType

  minIndexLat = interp_helper.closest_index(lats, y - cScope)
  maxIndexLat = interp_helper.closest_index(lats, y + cScope)
  minIndexLon = interp_helper.closest_index(lons, x - cScope)
  maxIndexLon = interp_helper.closest_index(lons, x + cScope)

  latLonList = []
  latLonTemp = []
  latLonList, latLonTemp = lon_lat_temp_lists(nf, minIndexLat, maxIndexLat, minIndexLon, maxIndexLon, len(deps), lats, lons, temperatureType)
  nf.close()
  return latLonTemp, deps, latLonList, time

def lon_lat_temp_lists(netFile, minIndexLat, maxIndexLat, minIndexLon,
                       maxIndexLon, depthRange, lats, lons, temperatureType):
  """
    Function is expecting 9 arguments:
      Dataset object for NetCDF 
      Integer for lowest index number in latitude points list
      Integer for highest index number in latitude points list
      Integer for lowest index number in longitude points list
      Integer for highest index number in longitude points list
      Integer for length of depth list
      List for latitude points in netCDF file
      List for longitude points in netCDF file
      String for name of depth temperatures (i.e. t_sd, t_an, temp)

    Objective:
      Call on a function based on the indices provided representing the
        minimum and maximum index number that will be used in the latitude
        list and longitude list, loops for every longitude/latitude points
        combination in the lists that will be used to find which points has
        any temperature data.
      After, check if longitude is near 0 point, call function again to
        append the opposite side of 0 longitude point along with their
        corresponding list of temperatures

    Return list of lists of latitude and longitude points, list of lists of
      temperatures
  """
  lonsLength = len(lons)
  latLonList = []
  latLonTemp = []
  moreLatLonList = []
  morelatLonTemp = []

  latLonList, latLonTemp = (
      organize_data(netFile, minIndexLat, maxIndexLat, minIndexLon,
                    maxIndexLon, 0, depthRange, lats, lons, temperatureType)
  )

  if (
        (0 <= minIndexLon <= 4) or
        (lonsLength - 5 <= maxIndexLon <= lonsLength - 1)
     ):
    if (0 <= minIndexLon <= 4):
      moreLatLonList, morelatLonTemp = (
          organize_data(netFile, minIndexLat, maxIndexLat, lonsLength - 5,
                        lonsLength - 2, -360, depthRange, lats, lons,
                        temperatureType)
      )
    elif (lonsLength - 5 <= maxIndexLon <= lonsLength - 1):
      moreLatLonList, morelatLonTemp = (
          organize_data(netFile, minIndexLat, maxIndexLat, 0, 4, 360,
                        depthRange, lats, lons, temperatureType)
      )
  return latLonList + moreLatLonList, latLonTemp + morelatLonTemp

def organize_data(netFile, minLatIndexNumber, maxLatIndexNumber,
                  minLonIndexNumber, maxLonIndexNumber, degrees,
                  dRange, lats, lons, tType):
  """
    Function is expecting 10 arguments:
      Dataset object for NetCDF 
      Integer for lowest index number in latitude points list
      Integer for highest index number in latitude points list
      Integer for lowest index number in longitude points list
      Integer for highest index number in longitude points list
      Integer for adding or subtracting longitude point to produce a new
        longitude point that is beyond file limits
      Integer for length of depth list
      List for latitude points in netCDF file
      List for longitude points in netCDF file
      String for name of depth temperatures (i.e. t_sd, t_an, temp)

    Process:
      Get the amount of longitude points that are going to be used
      Create a list of tuples that hold latitude and longitude index numbers
        and use it as an indicator map to locate coordinates in netcdf depth
        temperature
      Get longitude and latitude temperatures in netCDF which is returned as
        lists (each list represents a latitude point with longitude points
        from lowest to greatest) within lists (each list represents a depth
        from lowest to greatest) within one final list
      Loop through netcdf depth temperature list which is a list
        (longitudes for each latitude; lowest to greatest) within another
        list (depth starting at 0) encapsulated within another list
        If temperature is masked:
          replace it with nan (not a number)
        Find the matching coordinates to depth temperature and append it
          to list in dictionary
      Create new list of tuples that contains the actual latitude and
        longitude coordinates by looping through dictionary keys and using
        the index numbers within dictionary keys tuples

    Return list of lists of latitude and longitude points, list of lists of
      temperatures
  """
  latLonList = []
  latLonTemp = []
  latLonTempDict = {}
  numberOfLongitudes = len(range(minLonIndexNumber, maxLonIndexNumber+1))
  indicator = [ (y, x) for y in range(minLatIndexNumber, maxLatIndexNumber+1)
                       for x in range(minLonIndexNumber, maxLonIndexNumber+1)]
  oceanDepthData = netFile.variables[tType][0, 0:dRange,
                    minLatIndexNumber:maxLatIndexNumber+1,
                    minLonIndexNumber:maxLonIndexNumber+1]

  for oddata in oceanDepthData:
    for numY, ytemperatures in enumerate(oddata):
      for numX, xtemperature in enumerate(ytemperatures):
        indicatorNum = numY * numberOfLongitudes + numX
        indicatorKey = indicator[indicatorNum]

        if np.ma.is_masked(xtemperature):
          xtemperature = np.nan

        if indicatorKey in latLonTempDict:
          latLonTempDict[indicatorKey].append(xtemperature)
        else:
          latLonTempDict[indicatorKey] = [xtemperature]

  latLonList = [[lats[latLonIndexTuple[0]], lons[latLonIndexTuple[1]]+degrees] for latLonIndexTuple in list(latLonTempDict.keys())]
  
  return latLonList, list(latLonTempDict.values())

