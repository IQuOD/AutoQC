FROM continuumio/miniconda:latest

# set up conda and apt-get
RUN conda config --set always_yes yes --set changeps1 no
RUN conda update -q conda
RUN apt-get update

# dependencies!
RUN apt-get -y install libhdf5-serial-dev libnetcdf-dev unzip
RUN conda install --yes python=2.7 pip nose Shapely netCDF4 matplotlib numpy scipy pyproj pandas
RUN pip install wodpy cotede==0.15.3 gsw scikit-fuzzy pyWOA

# fetch & setup AutoQC + data
RUN git clone https://github.com/IQuOD/AutoQC.git
ADD EN_bgcheck_info.nc /AutoQC/data/.
ADD temperature_seasonal_5deg.nc /AutoQC/data/.
ADD etopo5.nc /AutoQC/data/.

