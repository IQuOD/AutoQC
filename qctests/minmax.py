import numpy, xarray, scipy.io, time, matplotlib.path
from util import obs_utils

def test(p, parameters):

    ## unpack profile data
    temp = p.t()

    temp_min, temp_max = extract_minmax(obs_utils.depth_to_pressure(p.z(), p.latitude()), p.longitude(), p.latitude())

    # true flag if temp is out of range
    qc = numpy.asarray([k<temp_min[i] or k>temp_max[i] for i,k in enumerate(temp)])

    return qc

def extract_minmax(pres, longitude, latitude):

    ## unpack minmax parameters
    minmax_temp = xarray.open_dataset('data/TEMP_MIN_MAX.nc')
    minmax_grid = xarray.open_dataset('data/GRID_MIN_MAX.nc')
    info_DGG = scipy.io.loadmat('data/info_DGG4H6.mat')
    lon = numpy.asarray([longitude])
    lat = numpy.asarray([latitude])
    hgrid_id = lonlat2indexISEA(lon, lat, info_DGG, '4H6')-1;

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

def lonlat2indexISEA(lon,lat,info_DGG4H,ISEA_type):
    # Add auxiliary information: list ISEA points per box
    if (ISEA_type == '4H7') | (ISEA_type == '4H6'):
       N0 = 10
    elif (ISEA_type == '4H5') | (ISEA_type == '4H4'):
       N0 = 20
    elif ISEA_type == '4H3':
       N0 = 30
    
    # Filter lat lon values
    latlon_filt = abs(lon)>999 
    if numpy.any(latlon_filt):
        lon[latlon_filt] = numpy.nan
        lat[latlon_filt] = numpy.nan
        del latlon_filt
    
    # Set lon between [-180 and 180]
    lon[lon>=180] = lon[lon>=180] - 360
    
    # Prepare box 
    ilon = numpy.floor((lon+180)/N0)+1
    ilat = numpy.floor((lat+90)/N0)+1
    condit=ilat>180/N0
    if sum(condit)>0:
          ilat[condit] = 180/N0
    ibox = numpy.ravel_multi_index(numpy.array([ilat,ilon]).astype(int),(int(180/N0),int(360/N0)),order='F',mode='wrap')
    
    kk = ~numpy.isnan(ibox)
    indexISEA = find_ISEA_box(lon[kk],lat[kk],numpy.vstack((ilat,ilon)).transpose(),ibox,info_DGG4H)

    return indexISEA

def find_ISEA_box(lon,lat,ilatlon,ibox,info_DGG4H):
    # initialise
    indexISEA = numpy.zeros(shape=lon.shape)
    iboxocc  = numpy.unique(ibox)
    for i in range(len(iboxocc)):
        list_ind = numpy.array(numpy.where(ibox == iboxocc[i]))[0]
        ll = len(list_ind)
        jlatlon = ilatlon[list_ind[0]].astype(int)    
        listISEAbox = info_DGG4H['list_ISEApts_in_boxes'][jlatlon[0]-1][jlatlon[1]-1][0][0].astype(int)
            
        # get lon lat
        clon = info_DGG4H['lon'][0][listISEAbox-1]
        clat = info_DGG4H['lat'][0][listISEAbox-1]
        lontt = lon[list_ind]
        lattt = lat[list_ind]

        # compute distance 
        dd = distance(lattt, lontt, numpy.repeat(clat[:,None],ll,axis=1),numpy.repeat(clon[:,None],ll,axis=1))
      
        isort = numpy.argsort(dd,axis=0)[0:3]
        list_bis=numpy.unique(listISEAbox[isort].flatten()-1) #ici
        
        for j in list_bis:

            #get lon lat
            clon = info_DGG4H['lon'][0][j]
            clat = info_DGG4H['lat'][0][j]
            # get vertices
            vlat0 = info_DGG4H['vertices']['lat'][0][0][:,j]
            vlon0 = info_DGG4H['vertices']['lon'][0][0][:,j]

            if vlon0.max() - vlon0.min()>100:
                vlon0[vlon0>0] = vlon0[vlon0>0] - 360
                
            ii = ~numpy.isnan(vlon0+vlat0)
            vlon0 = vlon0[ii]
            vlat0 = vlat0[ii]
    
            if abs(clat)!=90:
                vc1 = vlon0; vc2 = vlat0
                c1 = lontt; c2 = lattt
                if numpy.any(c1>max(vc1)):
                    c1[c1>max(vc1)] = c1[c1>max(vc1)]-360                    
                if numpy.any(c1<min(vc1)) :
                    c1[c1<min(vc1)] = c1[c1<min(vc1)]+360
                path = matplotlib.path.Path(numpy.vstack((vc1,vc2)).transpose())
                inside = path.contains_points(numpy.vstack((c1,c2)).transpose())
                indexISEA[list_ind[inside]] = j+1
                       
            else:
                ii = numpy.argsort(vlon0[0:-1])
                vc2 = vlat0[ii]
                vc1 = vlon0[ii]
                    
                vc1 = numpy.concatenate(([vc1[-1]-360], vc1, [vc1[0]+360], [vc1[0]+360],[vc1[-1]-360],[vc1[-1]-360]))
                vc2 = numpy.concatenate(([vc2[-1]], vc2, [vc2[0]], [clat+numpy.sign(clat)],[clat+numpy.sign(clat)],[vc2[-1]]));

                c1 = lontt
                c2 = lattt
                if numpy.any(c1>max(vc1)) :
                    c1[c1>max(vc1)] = c1[c1>max(vc1)]-360                    
                if numpy.any(c1<min(vc1)) != False:
                    c1[c1<min(vc1)] = c1[c1<min(vc1)]+360        
                path = matplotlib.path.Path(numpy.vstack((vc1,vc2)).transpose())
                inside = path.contains_points(numpy.vstack((c1,c2)).transpose())
                indexISEA[list_ind[inside]] = j+1                    
                    
    return indexISEA.astype(int)
        
def distance(lat1,lon1,lat2,lon2):
   lon1, lat1, lon2, lat2 = map(numpy.radians, [lon1, lat1, lon2, lat2])
   a = numpy.sin((lat2-lat1)/2)**2 + numpy.cos(lat1) * numpy.cos(lat2) * numpy.sin((lon2-lon1)/2)**2
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
