# install and configure environment for AutoQC
# Validated on 64bit ubuntu, kernel 4.4.0-1041-aws
# from inside AutoQC, run `bash install.sh`

# set up python environment
wget https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh -O miniconda.sh
bash miniconda.sh -b -p $PWD/miniconda
export PATH="$PWD/miniconda/bin:$PATH"
echo export 'PATH="'$PWD'/miniconda/bin:$PATH"' >> $HOME/.bashrc
rm miniconda.sh

# update all
conda config --set always_yes yes --set changeps1 no
conda update -q conda
sudo apt-get update -y

# install dependencies
sudo apt-get -y install libhdf5-serial-dev libnetcdf-dev unzip python-dev libgl1-mesa-glx python-qt4
conda install --yes python=2.7 pip nose \
                    Shapely=1.6.2 \
                    netCDF4=1.3.1 \
                    matplotlib=2.1.1 \
                    numpy=1.11.3 \
                    scipy=0.19.0 \
                    pyproj=1.9.5.1 \
                    pandas=0.21.1
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
