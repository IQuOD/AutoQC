FROM continuumio/miniconda:latest

# set up conda and apt-get
RUN conda config --set always_yes yes --set changeps1 no
RUN conda update -q conda
RUN apt-get update

# dependencies!
RUN apt-get -y install libhdf5-serial-dev libnetcdf-dev unzip
RUN conda install --yes python=2.7 pip nose Shapely netCDF4 matplotlib numpy scipy pyproj pandas
RUN pip install wodpy seabird cotede gsw scikit-fuzzy

# fetch & setup AutoQC + data
ADD master.zip /home/
RUN cd /home; unzip master.zip
ADD EN_bgcheck_info.nc /home/AutoQC-master/data/.
ADD temperature_seasonal_5deg.nc /home/AutoQC-master/data/.
ADD etopo5.nc /home/AutoQC-master/data/.


