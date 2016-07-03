FROM continuumio/miniconda:latest

# set up conda and apt-get
RUN conda config --set always_yes yes --set changeps1 no
RUN conda update -q conda
RUN apt-get update

# dependencies!
RUN apt-get -y install libhdf5-serial-dev libnetcdf-dev unzip postgresql libpq-dev python-dev nano
RUN conda install --yes python=2.7 pip nose Shapely netCDF4 matplotlib numpy scipy pyproj pandas

RUN pip install seabird>=0.6.3 gsw scikit-fuzzy psycopg2
# Pypi is not working well. Temporary solution
RUN pip install git+https://github.com/castelao/oceansdb.git@master#egg=oceansdb
RUN pip install git+https://github.com/castelao/CoTeDe.git@master#egg=CoTeDe
RUN pip install git+https://github.com/IQuOD/wodpy.git@master#egg=wodpy

# fetch & setup AutoQC + data
RUN git clone https://github.com/IQuOD/AutoQC.git
ADD EN_bgcheck_info.nc /AutoQC/data/.
ADD temperature_seasonal_5deg.nc /AutoQC/data/.
ADD woa13_decav_t13_5dv2.nc /AutoQC/data/.
ADD woa13_decav_t14_5dv2.nc /AutoQC/data/.
ADD woa13_decav_t15_5dv2.nc /AutoQC/data/.
ADD woa13_decav_t16_5dv2.nc /AutoQC/data/.
ADD woa13_decav_s13_5dv2.nc /AutoQC/data/.
ADD woa13_decav_s14_5dv2.nc /AutoQC/data/.
ADD woa13_decav_s15_5dv2.nc /AutoQC/data/.
ADD woa13_decav_s16_5dv2.nc /AutoQC/data/.
ADD etopo5.nc /AutoQC/data/.
ADD climatological_t_median_and_amd_for_aqc.nc /AutoQC/data/.

ADD bashrc /.bashrc
