# install and configure environment for AutoQC
# from inside AutoQC, run `bash install.sh`

# install apt-get packages
sudo apt-get update -y
sudo apt-get install -y nano bzip2 wget unzip \
    python2.7=2.7.12-1ubuntu0~16.04.3 \
    python-pip \
    libhdf5-serial-dev=1.8.16+docs-4ubuntu1 \
    libnetcdf-dev=1:4.4.0-2 \
    python-dev=2.7.12-1~16.04 \
    libgl1-mesa-glx=18.0.5-0ubuntu0~16.04.1 \
    python-qt4=4.11.4+dfsg-1build4 \
    python-tk=2.7.12-1~16.04

# install python packages
pip install Shapely==1.6.2 \
            netCDF4==1.3.1 \
            matplotlib==2.1.1 \
            pyproj==1.9.5.1 \
            pandas==0.21.1 \
            scipy==0.19.0 \
            numpy==1.11.3 \
            mkl==2018.0.3
pip install seabird==0.8.0 \
            gsw==3.0.3 \
            scikit-fuzzy==0.3 \
            oceansdb==0.6.0 \
            cotede==0.18.0 \
            wodpy==1.5.0

# Add AutoQC parameter files
cd data
wget http://www.metoffice.gov.uk/hadobs/en4/data/EN_bgcheck_info.nc
wget http://data.nodc.noaa.gov/thredds/fileServer/woa/WOA09/NetCDFdata/temperature_seasonal_5deg.nc
wget "http://oos.soest.hawaii.edu/thredds/ncss/etopo5?var=ROSE&disableLLSubset=on&disableProjSubset=on&horizStride=1&addLatLon=true" -O etopo5.nc 
wget http://data.nodc.noaa.gov/thredds/fileServer/woa/WOA13/DATAv2/temperature/netcdf/decav/5deg/woa13_decav_t13_5dv2.nc
wget http://data.nodc.noaa.gov/thredds/fileServer/woa/WOA13/DATAv2/temperature/netcdf/decav/5deg/woa13_decav_t14_5dv2.nc
wget http://data.nodc.noaa.gov/thredds/fileServer/woa/WOA13/DATAv2/temperature/netcdf/decav/5deg/woa13_decav_t15_5dv2.nc
wget http://data.nodc.noaa.gov/thredds/fileServer/woa/WOA13/DATAv2/temperature/netcdf/decav/5deg/woa13_decav_t16_5dv2.nc
wget https://data.nodc.noaa.gov/thredds/fileServer/woa/WOA13/DATAv2/salinity/netcdf/decav/5deg/woa13_decav_s13_5dv2.nc
wget https://data.nodc.noaa.gov/thredds/fileServer/woa/WOA13/DATAv2/salinity/netcdf/decav/5deg/woa13_decav_s14_5dv2.nc
wget https://data.nodc.noaa.gov/thredds/fileServer/woa/WOA13/DATAv2/salinity/netcdf/decav/5deg/woa13_decav_s15_5dv2.nc
wget https://data.nodc.noaa.gov/thredds/fileServer/woa/WOA13/DATAv2/salinity/netcdf/decav/5deg/woa13_decav_s16_5dv2.nc
# TBD climatological_t_median_and_amd_for_aqc.nc
cd ..

export OCEANSDB_DIR=$PWD/data/
echo export 'OCEANSDB_DIR='$PWD'/data/' >> $HOME/.bashrc
