AutoQC
======

[![Build Status](https://travis-ci.org/IQuOD/AutoQC.svg?branch=master)](https://travis-ci.org/IQuOD/AutoQC)

##Introduction

Recent studies suggest that changes to global climate as have been seen at the Earth's land and ocean surface are also making their way into the deep ocean, which is the largest active storage system for heat and carbon available on the timescale of a human lifetime. Historical measurements of subsurface ocean temperature are essential to the scientific research investigating the changes in the amount of heat stored in the ocean and also to other climate research activities such as combining observations with numerical models to provide estimates of the global ocean's and Earth's climate state  in the past and predictions for the future. Unfortunately, as with all observations, these measurements contain errors and biases that must be identified to prevent a negative impact on the applications and investigations that rely on them. Various groups from around the world have developed quality control tests to perform this important task. However, this has led to duplication of effort, code that is not easily available to other researchers and the introduction of climate model differences solely due to the varying performance of these software systems whose nuances relative to one another are poorly known.

Recently, an international team of researchers has decided to work together to break down the barriers between the various groups and countries through the formation of the IQuOD (International Quality Controlled Dataset) initiative. One of the key aims is to intercompare the performance of the various automatic quality control tests that are presently being run to determine a best performing set. This work has started. However, it currently involves individuals running test datasets through their own systems and is being confounded by complications associated with the differences in the file formats and systems that are in use in the various labs and countries.

The IQuOD proposal is to set up an open quality control benchmarking system.  Work will begin by implementing a battery of simple tests to run on some test data, and producing summary statistics and visualizations of the results.  Later goals include helping researchers either wrap their existing C, Fortran and MATLAB test functions in Python for use in this test suite, or re-implementing those tests in native Python.

## Dependencies & Setup:

The easiest way to set up AutoQC is via [Docker](https://www.docker.com/); install Docker per their website, and then grab the autoqc image:

```
docker pull iquod/autoqc
```

Start the image via

```
docker run -i -t iquod/autoqc /bin/bash
```

And you'll find AutoQC all set up and ready to use in the directory `/AutoQC`. Note that the version of AutoQC that ships with the docker image may be behind master on GitHub; you can always do `git pull origin master` from the `/AutoQC` directory inside the image, if you need an update.

If you want to run AutoQC without Docker, have a look at the setup steps in `docker/Dockerfile`; these correspond to the same setup steps you'll need to do on a similar machine (i.e. on Debian with miniconda already installed).

Docker makes it very convenient for the project to run AutoQC, but note that the data files to run the full set of AutoQC checks are obtained as detailed below:

 - EN_bgcheck_info.nc (http://www.metoffice.gov.uk/hadobs/en4) from http://www.metoffice.gov.uk/hadobs/en4/data/EN_bgcheck_info.nc;
 - temperature_seasonal_5deg.nc (https://www.nodc.noaa.gov/OC5/indprod.html) from http://data.nodc.noaa.gov/thredds/fileServer/woa/WOA09/NetCDFdata/temperature_seasonal_5deg.nc;
 - etopo5.nc (http://www.ngdc.noaa.gov/mgg/global/etopo5.HTML) from http://oos.soest.hawaii.edu/thredds/ncss/etopo5?var=ROSE&disableLLSubset=on&disableProjSubset=on&horizStride=1&addLatLon=true;
 - climatological_t_median_and_amd_for_aqc.nc: based on climatological_t_median_and_amd_for_aqc.dat provided by Viktor Gouretski, Integrated Climate Data Center, University of Hamburg, Hamburg, Germany, February 2016.
 - Seasonal WOA13 files (http://data.nodc.noaa.gov/thredds/fileServer/woa/WOA13/DATAv2/temperature/netcdf/decav/5deg/):
   - woa13_decav_t13_5dv2.nc
   - woa13_decav_t14_5dv2.nc
   - woa13_decav_t15_5dv2.nc
   - woa13_decav_t16_5dv2.nc

### AutoQC on AWS

Docker makes running AutoQC on the cloud very easy. Once you've set up your Amazon Web Services account, launch an EC2 instance and do:

```
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo docker pull iquod/autoqc
sudo docker run -i -t iquod/autoqc /bin/bash
```

And once again, AutoQC will be all set up in `/AutoQC`.

##Usage
To execute the quality control checks,
`python AutoQC.py name nProcessors`

where `name` names the output csv naming as `result-name.csv`, and `nProcessors` is the number of cores to parallelize over.

##Structure
`AutoQC.py` performs the following:
 - automatically detects all quality control tests found in `/qctests`
 - takes the list of raw data files from `datafiles.json`, and decodes their contents into an array of profile objects
 - runs all the automatically detected tests over each of these profiles
 - return an array for each test indicating which profiles excpetions were raised for, and an array indicating the expected result for each profile

###Testing Data
Each quality control test must be written as its own file in `/qctests`, of the form `def test(p)`, where `p` is a profile object; each test returns a bool, where `True` indicates the test has *failed*.

###Testing Code
To run the code tests:

```
pip install nose
nosetests tests/*.py
```

###Data
Each data file listed in `datafiles.json` is in the World Ocean Database (WOD; http://www.nodc.noaa.gov/OC5/WOD/pr_wod.html) ASCII format.

###Profile Objects Specification
See [the docs](https://github.com/IQuOD/AutoQC/blob/master/dataio/README.md) for the WodProfile class, a decoding helper for the WOD ASCII format.

##Contributing
Quality control checks waiting to be implemented are listed in the Issues. If you would like to work on coding up a check, please assign yourself to the issue to avoid others duplicating the effort.
