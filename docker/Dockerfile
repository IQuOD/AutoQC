FROM continuumio/miniconda:latest

# set up conda and apt-get
RUN conda config --set always_yes yes --set changeps1 no
RUN conda update -q conda
RUN apt-get update

# dependencies!
RUN apt-get -y install libhdf5-serial-dev libnetcdf-dev unzip
RUN conda install --yes python=2.7 pip nose Shapely netCDF4 matplotlib numpy scipy pyproj pandas
#RUN pip install wodpy>=1.3.0 cotede>=0.15.4 gsw scikit-fuzzy pyWOA>=0.1.2
RUN pip install wodpy cotede gsw scikit-fuzzy pyWOA
# Temporary solution while pypi doesn't fix its index.
RUN pip install --upgrade wodpy cotede pyWOA

# fetch & setup AutoQC + data
RUN git clone https://github.com/IQuOD/AutoQC.git
ADD EN_bgcheck_info.nc /AutoQC/data/.
ADD temperature_seasonal_5deg.nc /AutoQC/data/.
ADD etopo5.nc /AutoQC/data/.
ADD climatological_t_median_and_amd_for_aqc.nc /AutoQC/data/.

