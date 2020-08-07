# install and configure environment for AutoQC
# from inside AutoQC, run `bash install.sh`

# install apt-get packages
apt-get update -y
apt-get install -y nano bzip2 wget unzip \
    python3.6 \
    python3-pip \
    libhdf5-serial-dev \
    libnetcdf-dev \
    python3-dev \
    libgl1-mesa-glx
    #python-qt4=4.12.1+dfsg-2 \
    #python-tk=2.7.12-1~16.04

# install python packages
pip3 install Shapely==1.6.4.post2 \
            netCDF4==1.5.1.2 \
            matplotlib==3.1.0 \
            pyproj==2.1.3 \
            pandas==0.21.1 \
            scipy==0.18.1 \
            mkl==2019.0
pip3 install seabird==0.11.0 \
            gsw==3.0.3 \
            scikit-fuzzy==0.4.1 \
            oceansdb==0.8.6 \
            cotede==0.22.1 \
            wodpy==1.6.1 \
            numpy==1.11.3

# Add AutoQC parameter files
# note many of these links are broken; we leave them here until replacements are found,
# and bake the corresponding data files into the containerized environment for posterity.
#cd data
#wget http://www.metoffice.gov.uk/hadobs/en4/data/EN_bgcheck_info.nc
#wget http://data.nodc.noaa.gov/thredds/fileServer/woa/WOA09/NetCDFdata/temperature_seasonal_5deg.nc
#wget "http://oos.soest.hawaii.edu/thredds/ncss/etopo5?var=ROSE&disableLLSubset=on&disableProjSubset=on&horizStride=1&addLatLon=true" -O etopo5.nc 
#wget http://data.nodc.noaa.gov/thredds/fileServer/woa/WOA13/DATAv2/temperature/netcdf/decav/5deg/woa13_decav_t13_5dv2.nc
#wget http://data.nodc.noaa.gov/thredds/fileServer/woa/WOA13/DATAv2/temperature/netcdf/decav/5deg/woa13_decav_t14_5dv2.nc
#wget http://data.nodc.noaa.gov/thredds/fileServer/woa/WOA13/DATAv2/temperature/netcdf/decav/5deg/woa13_decav_t15_5dv2.nc
#wget http://data.nodc.noaa.gov/thredds/fileServer/woa/WOA13/DATAv2/temperature/netcdf/decav/5deg/woa13_decav_t16_5dv2.nc
#wget https://data.nodc.noaa.gov/thredds/fileServer/woa/WOA13/DATAv2/salinity/netcdf/decav/5deg/woa13_decav_s13_5dv2.nc
#wget https://data.nodc.noaa.gov/thredds/fileServer/woa/WOA13/DATAv2/salinity/netcdf/decav/5deg/woa13_decav_s14_5dv2.nc
#wget https://data.nodc.noaa.gov/thredds/fileServer/woa/WOA13/DATAv2/salinity/netcdf/decav/5deg/woa13_decav_s15_5dv2.nc
#wget https://data.nodc.noaa.gov/thredds/fileServer/woa/WOA13/DATAv2/salinity/netcdf/decav/5deg/woa13_decav_s16_5dv2.nc
#wget ftp://ftp.aoml.noaa.gov/phod/pub/bringas/XBT/AQC/AOML_AQC_2018/data_center/woa13_00_025.nc
#wget https://s3-us-west-2.amazonaws.com/autoqc/climatological_t_median_and_amd_for_aqc.nc
#cd ..

export OCEANSDB_DIR=$PWD/data/
echo export 'OCEANSDB_DIR='$PWD'/data/' >> $HOME/.bashrc