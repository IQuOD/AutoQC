import numpy, xarray, scipy.io, time, matplotlib.path
from util import obs_utils

def test(p, parameters):

    ## unpack profile data
    temp = p.t()
    temp_min, temp_max = extract_minmax(-obs_utils.depth_to_pressure(p.z(), p.latitude()), p.longitude(), p.latitude())
    print(temp_min, temp_max)

    # true flag if temp is out of range
    qc = numpy.zeros(p.n_levels(), dtype=bool)
    for i, k in enumerate(temp):
        # Only define a QC flag if all parameters are available.
        if numpy.ma.is_masked(k) or numpy.isnan(temp_min[i]) or numpy.isnan(temp_max[i]):
            continue
        qc[i] = (k<temp_min[i]) or (k>temp_max[i])

    return qc

def extract_minmax(pres, longitude, latitude):
    ## unpack minmax parameters, downloadable from https://www.seanoe.org/data/00660/77199/
    minmax_temp = xarray.open_dataset('data/TEMP_MIN_MAX.nc')
    minmax_grid = xarray.open_dataset('data/GRID_MIN_MAX.nc')
    info_DGG = scipy.io.loadmat('data/info_DGG4H6.mat')
    lon = numpy.asarray([longitude])
    lat = numpy.asarray([latitude])
    hgrid_id = lon_lat_to_min_max_index(lon, lat, info_DGG, '4H6')

    layer_id = numpy.empty((pres.shape))
    layer_id[:] = numpy.NaN
    temp_min = numpy.empty((pres.shape))
    temp_min[:] = numpy.NaN
    temp_max = numpy.empty((pres.shape))
    temp_max[:] = numpy.NaN

    ## determine minmax range
    layer_id = val2index(pres, minmax_temp.depth.data)
    nonan = ~numpy.isnan(layer_id)
    temp_min[numpy.where(nonan)[0]] = minmax_temp.temp_min.data[hgrid_id,layer_id[nonan].astype(int)]
    temp_max[numpy.where(nonan)[0]] = minmax_temp.temp_max.data[hgrid_id,layer_id[nonan].astype(int)]
    return temp_min, temp_max

def lon_lat_to_min_max_index(longitude, latitude, info_file, isea_type):
    """
    Function which takes a latitude and longitude point and returns the cell
    index on the min-max grid. The longitude and latitude arrays must have the
    same dimensions.

    Args:
        * longitude (numpy.ndarray): Longitude values (will be transformed to be
            on -180, 180 if outside this range).
        * latitude (numpy.ndarray): Latitude values.
        * info_file (dict): An imported matlab file containing information
            about the min-max grids e.g. number of points contributing to the
            fields, vertices of the cells etc.
        * isea_type (string): This is part of the info_file name and is used
            to determine the resolution of the lower-res grid boxes used for
            speeding up the process to find the right grid box.

    Returns:
        * index_isea (numpy.ndarray): The integer values of the min max grid
            boxes containing the given latitude-longitude points.

    """

    ISEA_TYPE_TO_GRID_BOX_SIZE = {'4H7': 10, '4H6': 10, '4H5': 20, '4H4': 20, '4H3': 30}

    # low_res_size is the size of the larger grid boxes, (10 by 10 normally),
    # used to speed up the search for the exact (110km grid box) that the points
    # are in (this variable was called N0 in the original CMEMS code):
    low_res_size = ISEA_TYPE_TO_GRID_BOX_SIZE[isea_type]

    # Filter lat lon values to remove any that are spurious (given that these
    # are from the analysis grid boxes this should never be needed!):
    lat, lon = filter_lat_lon(latitude, longitude)

    # Set lon between [-180 and 180]
    lon[lon >= 180] = lon[lon >= 180] - 360

    # Get the grid indices for each lat/lon on the N0 by N0 grid:
    ilon, ilat = get_low_res_min_max_grid_indices(lon, lat, low_res_size)

    # Check that the values are in the grid expected (we only do this for
    # latitude as longitude has already been constrained to be in the range
    # expected):
    check_lat_range = ilat > 180 / low_res_size
    if sum(check_lat_range) > 0:
        print('WARNING: Latitude was not in expected range and may not have '
              'been assigned to the correct grid box.')
        ilat[check_lat_range] = 180 / low_res_size

    # Take the N0 by N0 degree grid box indices and using a column-major
    # ordering return an array of indices into the flattened version of an
    # array of dimensions (180/N0, 360/N0). This is a recognised Python function
    # and is therefore not tested:
    box_indices = numpy.ravel_multi_index(numpy.array([ilat, ilon]).astype(int),
                                       (int(180 / low_res_size),
                                        int(360 / low_res_size)),
                                       order='F', mode='wrap')

    # Select only indices where the value is not missing:
    non_missing_locations = ~numpy.isnan(box_indices)

    # Now use these indices to find the hexagonal grid box indices:
    index_isea = find_min_max_gridbox(lon[non_missing_locations],
                                      lat[non_missing_locations],
                                      numpy.vstack((ilat, ilon)).transpose(),
                                      box_indices, info_file)

    return index_isea


def filter_lat_lon(lat, lon, filter_threshold=999):
    """
    Filter lat lon values to remove any that are spurious. In the CMEMS version
    this only filtered longitudes, but it makes most sense to filter latitudes
    as well.

    Args:
        * lat (numpy.ndarray): Latitude values.
        * lon (numpy.ndarray): Longitude values (will be transformed to be
            on -180, 180 if outside this range).
        * filter_threshold (int): The threshold of acceptable values before
            longitudes or latitudes are deemed incorrect.

    Returns:
        * lat (numpy.ndarray): The latitude values with any points where lat or
            lon were beyond the filter_threshold removed.
        * lon (numpy.ndarray): The longitude values with any points where lat or
            lon were beyond the filter_threshold removed.

    """

    lat_lon_filtered = numpy.logical_or(abs(lon) > filter_threshold,
                                     abs(lat) > filter_threshold)
    if numpy.any(lat_lon_filtered):
        lat[lat_lon_filtered] = numpy.nan
        lon[lat_lon_filtered] = numpy.nan
        del lat_lon_filtered

    return lat, lon


def get_low_res_min_max_grid_indices(lon, lat, grid_size):
    """
    Get the broader min_max grid index when the interest is in finding the low
    resolution grid box that a latitude-longitude point falls in.

    Args:
        * lon (numpy.ndarray): The longitude points (on [-180, 180]).
        * lat (numpy.ndarray): The latitude points (on [-90, 90]).
        * grid_size (int): The low resolution grid box size.

    Returns:
        * lon_index (numpy.ndarray): The longitude indices for the low
            resolution grid boxes.
        * lat_index (numpy.ndarray): The latitude indices for the low resolution
            grid boxes.
    """

    # Go from the longitude, latitude values to the grid boxes they would fall
    # in:
    # TODO: This code was translated from matlab which starts indexing at 1,
    #  it would be good to assess where +1 and -1 values can therefore be
    #  removed to make it more pythonic.
    lon_index = numpy.floor((lon + 180) / grid_size) + 1
    lat_index = numpy.floor((lat + 90) / grid_size) + 1

    return lon_index, lat_index

def find_min_max_gridbox(lon, lat, lat_lon_indices, box_index, info_file):
    """
    From the low resolution latitude and longitude grid produced in
    lon_lat_to_min_max_index find the corresponding grid box in the main min-max
    grid.

    Args:
        * lon (numpy.ndarray): The longitudes as provided in profiles/analyses.
        * lat (numpy.ndarray): The latitudes as provided in profiles/analyses.
        * lat_lon_indices (numpy.ndarray): The lat-lon indices on a low res
            grid (with 180, -90 as the starting point and counting up in
            columns).
        * box_index (numpy.ndarray): The grid box index of each point on the
            low resolution grid.
        * info_file (dict): The information about the grid, read in from Matlab.

    Returns:
        * index_isea (int in a numpy.ndarray): The indices of the lat-lon points
            in the hexagonal min-max grid.

    """

    FILL_VALUE = 99999.

    # TODO: This function currently contains loops within loops it would be good
    #  better understand the min-max grid structure so it can be further split
    #  up and tested.

    # Set up an array which is all fill_value, which will be populated with the
    # indices:
    index_isea = numpy.full(shape=lon.shape, fill_value=FILL_VALUE)

    # There will be occurrences of the same grid box and we only want to do the
    # transformation on to the min max grid once, then store for all lat-lons in
    # that grid box:
    iboxocc = numpy.unique(box_index)

    # Now loop over these unique grid boxes:
    for b, box in enumerate(iboxocc):

        # Find all the lat-lon indices that are in this grid box:
        list_ind = numpy.asarray((box_index == box).nonzero())[0]

        # Find out how many indices there are:
        list_length = len(list_ind)

        # Get the index of the first of these points on the low resolution grid:
        lat_lon_index = lat_lon_indices[list_ind[0]].astype(int)

        # I think this reads in all the min-max grid point indices in the low
        # resolution grid box from the provided CMEMS index file:
        list_isea_box = (
            info_file['list_ISEApts_in_boxes'][lat_lon_index[0] - 1]
            [lat_lon_index[1] - 1][0][0].astype(int))

        # Read in the central longitude and latitude of each min-max grid cell
        # in the low resolution box:
        clon = info_file['lon'][0][list_isea_box - 1]
        clat = info_file['lat'][0][list_isea_box - 1]

        # Get the observed longitudes and latitudes that fall in the 10 by 10
        # grid box:
        obs_lon = lon[list_ind]
        obs_lat = lat[list_ind]

        # Compute the distance between each observed lat-lon point and the
        # centre of each grid box that falls into the low resolution grid box:
        distances = distance(obs_lat, obs_lon,
                             numpy.repeat(clat[:, None], list_length, axis=1),
                             numpy.repeat(clon[:, None], list_length, axis=1))

        # Get the indies of the three smallest distances (I think):
        closest_indices = numpy.argsort(distances, axis=0)[0:3]

        # Find the unique min-max grid box indices that are the closest (or near
        # closest) to at least one of the observed latitudes and longitudes:
        list_bis = numpy.unique(list_isea_box[closest_indices].flatten() - 1)

        # For each of these selected grid boxes:
        for j in list_bis:
            # Get the vertices of this grid box from the CMEMS Matlab file:
            vlat0 = info_file['vertices']['lat'][0][0][:, j]
            vlon0 = info_file['vertices']['lon'][0][0][:, j]

            # Account for the possibility of the longitude box spanning the
            # date line:
            if vlon0.max() - vlon0.min() > 100:
                vlon0[vlon0 > 0] = vlon0[vlon0 > 0] - 360

            # Check that all the vertices are valid:
            valid_vertices = ~numpy.isnan(vlon0 + vlat0)
            vlon0 = vlon0[valid_vertices]
            vlat0 = vlat0[valid_vertices]

            # Get the central latitude of this grid box and check that it isn't
            # 90S or 90N:
            central_lat = info_file['lat'][0][j]

            # Check that the central latitude isn't 90N or 90S:
            if abs(central_lat) != 90:
                # Get the longitude and latitude of the vertices and the lons
                # and lats of the observed points:
                vc1 = vlon0
                vc2 = vlat0
            # If the central latitude is 90N or 90S:
            else:
                # Re-organise the vertices:
                re_index = numpy.argsort(vlon0[0:-1])
                vc2 = vlat0[re_index]
                vc1 = vlon0[re_index]

                # Transform the vertices:
                vc1 = numpy.concatenate(([vc1[-1] - 360], vc1, [vc1[0] + 360],
                                      [vc1[0] + 360], [vc1[-1] - 360],
                                      [vc1[-1] - 360]))
                vc2 = numpy.concatenate(([vc2[-1]], vc2, [vc2[0]],
                                      [central_lat + numpy.sign(central_lat)],
                                      [central_lat + numpy.sign(central_lat)],
                                      [vc2[-1]]))

            # Check the observed longitudes are in the correct range and adjust
            # if not:
            if numpy.any(obs_lon > max(vc1)):
                obs_lon[obs_lon > max(vc1)] = obs_lon[obs_lon > max(vc1)] - 360
            if numpy.any(obs_lon < min(vc1)):
                obs_lon[obs_lon < min(vc1)] = obs_lon[obs_lon < min(vc1)] + 360

            # Form a path from the vertices:
            path = matplotlib.path.Path(numpy.vstack((vc1, vc2)).transpose())

            # See which of the lat-lon points are contained in this min-max
            # grid box:
            inside = path.contains_points(numpy.vstack((obs_lon, obs_lat)
                                                    ).transpose())

            # For all 'True' values of inside, store j as the min-max grid box
            # index (changed from j+1 in original minmax code as we index in
            # Python not Matlab):
            index_isea[list_ind[inside]] = j

    # Ensure that all elements of indexISEA have been filled and raise an error
    # if not:
    if numpy.any(index_isea == FILL_VALUE):
        raise ValueError('Min_max grid box indices have not been found for all '
                         'input lat-lon pairs.')

    return index_isea.astype(int)

def distance(observed_lats, observed_lons, central_lats, central_lons):
    """
    Function to calculate the distance between each observed lat and lon and
    the centre of each min-max grid box. distance is a slightly misleading name,
    angle would be a better name for this function, but distance is being kept
    for traceability back to the CMEMS code it was created from.

    Args:
        * observed_lats (numpy.ndarray): The latitudes observed.
        * observed_lons (numpy.ndarray): The longitudes observed.
        * central_lats (numpy.ndarray): The central latitudes array repeated as
            many times as there are observed_lats.
        * central_lons (numpy.ndarray): The central longitudes array repeated as
            many times as there are observed_lons.

    Returns:
        * rng (numpy.ndarray): The angle between each pair of observed points
            and central longitudes in degrees.
    """

    # Using the inbuilt map function convert all the observed and central lat
    # and long values to be in radians:
    lon1, lat1, lon2, lat2 = map(numpy.radians, [observed_lons, observed_lats,
                                              central_lons, central_lats])

    # Get the angle between the all pairs of points (in radians):
    a = (numpy.sin((lat2 - lat1)/2)**2
         + numpy.cos(lat1) * numpy.cos(lat2) * numpy.sin((lon2 - lon1)/2)**2)
    rng = 2 * numpy.arctan(numpy.sqrt(a)/numpy.sqrt(1 - a))

    return numpy.degrees(rng)

def val2index(VALs_orig,val_tab):
    nd = len(val_tab);
    VALs_size = VALs_orig.shape[0];
    VALs_m = numpy.ones((nd-1,VALs_size))*VALs_orig
    valm = val_tab[0:-1];
    valp = val_tab[1:];
    valm_m = numpy.transpose(numpy.ones((VALs_size,nd-1))*valm)
    valp_m = numpy.transpose(numpy.ones((VALs_size,nd-1))*valp)
    ii = numpy.transpose(numpy.ones((VALs_size,nd-1))*numpy.arange(0,nd-1))
    is_ok = (VALs_m > valm_m) & (VALs_m <= valp_m);
    index = sum(ii*is_ok);
    VALs_out = (VALs_orig <= valm[0]) | (VALs_orig > valp[-1]);
    index[VALs_out] = 'nan';
    index[numpy.isnan(VALs_orig)] = 'nan'
    index = numpy.reshape(index,VALs_size);
    return index
