#!/usr/bin/env python
#
# Author: Patrick Halsall

import sys
import numpy as np
from scipy import interpolate, spatial

def closest_index(coordinateList, point):
  """
    Find the index of the element in coordinateList closest to point 

    coordinateList: list of floats
    point: value of interest
  """

  return int(np.abs(np.array(coordinateList)-point).argmin())

def get_index_and_next(lList, plot):
  """
    return two list indices in order: the index i of the value closest to <plot>, 
    and the next index if <plot> > lList[i],
    or the previous if <plot> < lList[i].

    lList: list of floats
    plot: float
  """

  index1 = closest_index(lList, plot)
  if index1 == 0:
    index2 = 1
  elif index1 == len(lList)-1 or lList[index1] > plot:
    index2 = index1-1
  else:
    index2 = index1+1

  if index1 >= index2:
    return index2, index1
  else:
    return index1, index2

def indices_without_nan(i, j, v1, v2):
  """
  find and return all indices k of v1 such that v2[k][i] and v2[k][j] both exist and are not nan

  i: int
  j: int
  v1: list
  v2: list
  """

  acceptableIndices = []
  for indx, x in enumerate(v1):
    if (
          (i > len(v2[indx]) - 1) or
          (j > len(v2[indx]) - 1) or
          (np.isnan(v2[indx][i])) or
          (np.isnan(v2[indx][j]))
       ):
        pass
    else:
        acceptableIndices.append(indx)
  return acceptableIndices

def interpolate_with_interp1d(x0, x, y):
  """
  Construct y = f(x) as a linear interpolation between x and y,
  and return f(x0), or 99999.99 if f(x0) is nan.

  x0: float
  x: list of floats
  y: list of floats  
  """

  f = interpolate.interp1d(x, y)
  d = f([x0])[0]
  if np.isnan(d):
    return 99999.99
  else:
    return d

def nearest_indices(y, x, latLonList, amountNearNeighbors):
  """
    Function is expecting 4 arguments:
      Float for longitude
      Float for latitude
      List of lists with latitude and longitude
      Integer for the most amount of coordinate index numbers to return

    Process:
      Create kd-tree for quick nearest-neighbor lookup
      Query the kd-tree for nearest neighbors with amountNearNeighbors
        parameter to return approximate nearest neighbors

    Return list of distances and list of index numbers of the nearest
      neighbors to coordinate
  """

  tree = spatial.cKDTree(latLonList)
  return tree.query([y,x], min(amountNearNeighbors, len(latLonList)) )

def temperature_interpolation_process(x, y, depth, depthColumns, llList,
                                      llTempList, zeroDepthMissing,
                                      tempType):
  """
    Function is expecting 8 arguments:
      Float for longitude
      Float for latitude
      Float for depth
      List for depth measurements
      List of lists for latitude and longitude tuples
      List of lists for temperatures
      Boolean for whether or not to repeat the first depth column (weekly
        analysis depth starts at 5 meters instead of 0)
      String for name of type of climatology

    Process:
      Get index numbers in depth measurements that will insure a depth
        measurement that is greater than observation depth and a depth
        measurement that is less than main depth. This will help create the
        vertical and horizontal axes for the 1-D interpolation process
      Find every latitude and longitude coordinates that has data and get
        their index numbers from a list of lists that contain a tuple with
        latitude and longitude coordinates
      Loop through the index numbers indicating list with acceptable data to
        create a new list of lists list of lists that contain a tuple with
        latitude and longitude coordinates and another new list of lists the
        contain temperature measurements
      Find the nearest latitude and longitude coordinates from the main
        latitude and longitude coordinate
      If the nearest latitude and longitude coordinate is less than or
        equal to 0.25:
        Get the latitude and longitude coordinate's temperature measurements
          (only the depth measurements that is one greater and one lesser
          than the observation depth)
        Get the netCDF depth measurement header list (only the depth
          measurements that is one greater and one lesser than the
          observation depth)
        Check if the lowest depth is the first depth measuremnt and also,
          if it is analyzing weekly analysis data so that copy of the first
          depth and be added to the beginning of the depth temperature
          measurement list (weekly analysis does not have a 0 depth
          temperature measurement)
        Interpolate a 1-D function to get a temperature between two known
          ocean depth temperatures
      Else
        Return 99999.99

    Return 99999.99 if depth is greater than netCDF measurement depth list
    Return a temperature that has been interpolated
  """

  # find depths bracketing the depth of interest
  depIndex1, depIndex2 = get_index_and_next(depthColumns, depth)
  if depth > depthColumns[depIndex2]:
    return 99999.99

  # find all valid lat, lon, and temperatures at this depth bracket
  indicesNotNanList = indices_without_nan(depIndex1, depIndex2, llList, llTempList)
  nonanllList = [llList[indx] for indx in indicesNotNanList]
  nonanllTempList = [llTempList[indx] for indx in indicesNotNanList]

  # find the nearest point from the list above to the point of interest
  numberOfNeighbors = 1
  if nonanllList:
    distancesList, locationIndicesList = nearest_indices(y, x, nonanllList, numberOfNeighbors)
    nearestRadDistance = distancesList
    nearestIndex = locationIndicesList
  else:
    return 99999.99

  if (0.0 <= nearestRadDistance <= 0.25):
    tempByDepth = nonanllTempList[nearestIndex][depIndex1:depIndex2+1]
    depthColumnsSection = [depthColumns[depIndex1], depthColumns[depIndex2]]
    if depIndex1 == 0 and zeroDepthMissing:
      depthColumnsSection.insert(0, 0.0)
      tempByDepth.insert(0, tempByDepth[depIndex1])
    if (tempType == "climaInterpStandardDev"):
      depthColumnsSection = np.array(depthColumnsSection).clip(min=0)
    interpDepthTemp = interpolate_with_interp1d(depth, depthColumnsSection,tempByDepth)
    return interpDepthTemp
  else:
    return 99999.99

