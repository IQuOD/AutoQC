AutoQC
======

[![Build Status](https://travis-ci.org/IQuOD/AutoQC.svg?branch=master)](https://travis-ci.org/IQuOD/AutoQC)

##Introduction

Recent studies suggest that changes to global climate as have been seen at the Earth's land and ocean surface are also making their way into the deep ocean, which is the largest active storage system for heat and carbon available on the timescale of a human lifetime. Historical measurements of subsurface ocean temperature are essential to the scientific research investigating the changes in the amount of heat stored in the ocean and also to other climate research activities such as combining observations with numerical models to provide estimates of the global ocean's and Earth's climate state  in the past and predictions for the future. Unfortunately, as with all observations, these measurements contain errors and biases that must be identified to prevent a negative impact on the applications and investigations that rely on them. Various groups from around the world have developed quality control tests to perform this important task. However, this has led to duplication of effort, code that is not easily available to other researchers and the introduction of climate model differences solely due to the varying performance of these software systems whose nuances relative to one another are poorly known.

Recently, an international team of researchers has decided to work together to break down the barriers between the various groups and countries through the formation of the IQuOD (International Quality Controlled Dataset) initiative. One of the key aims is to intercompare the performance of the various automatic quality control tests that are presently being run to determine a best performing set. This work has started. However, it currently involves individuals running test datasets through their own systems and is being confounded by complications associated with the differences in the file formats and systems that are in use in the various labs and countries.

The IQuOD proposal is to set up an open quality control benchmarking system.  Work will begin by implementing a battery of simple tests to run on some test data, and producing summary statistics and visualizations of the results.  Later goals include helping researchers either wrap their existing C, Fortran and MATLAB test functions in Python for use in this test suite, or re-implementing those tests in native Python.

## Dependencies & Setup:

### Local Install

 **Tested on Ubuntu 16.04**

 To clone this project and set it up, make sure `git` is installed, then:

 ```
 $ git clone https://github.com/IQuOD/AutoQC
 $ cd AutoQC
 $ source install.sh
 ```

### Containerized Install

 To run AutoQC in a containerized environment, make sure `docker` is installed, then:

 ```
 $ docker image run -it -v /my/data/directory:/rawdata iquod/autoqc:ubuntu-16.04 bash
 ```

 Anything in `/my/daya/directory` on your machine will be available at `/rawdata` inside the container, and vice versa. Use this to add raw WOD-ASCII data to your container, and add multiple `-v origin:destination` paths to include multiple directories in the same way.

 You may also want to `git pull origin master` inside the `/AutoQC` directory inside your container, to fetch the latest version of the project.

##Usage

AutoQC runs in three steps: database construction, qc running, and result summarization.

### Database Construction

```
python build-db.py filename tablename
```

Where `filename` is the name of a WOD-ascii file to read profiles from, and `tablename` is the name of a postgres table to write the results to; `tablename` will be created if it doesn't
exist, or appended to if it does. `tablename` will have the following columns:

column name | description
------------|-----------
`raw`       | the raw WOD-ASCII text originally found in the input file
`truth`     | whether any temperature qc levels were flagged at 3 or greater
`uid`       | unique profile serial number
`year`      | timestamp year
`month`     | timestamp month, integers [1,12]
`day`       | timestamp day, integers [1,31]
`time`      | timestamp walltime, real [0,24)
`lat`       | profile latitude
`long`      | profile longitude
`cruise`    | cruise id
`probe`     | probe index, per WOD specifications

Additionally, there is a column in the table for the qc results of every test found in the `/qctests` directory; these columns are filled in in the next step.

### QC Execution

```
python AutoQC.py tablename nProcessors
```

where `tablename` is the postgres table to pull profiles from (probably the same as `tablename` in the last step), and `nProcessors` is how many processors you'd like to parallelize over.

### Result Summary

```
python summarize-results.py tablename
```

where `tablename` is the postgres table used in the previous steps. A summary of true flags, true passes, false positives and false negatives is generated for each test.


##Testing

###Testing Data
Each quality control test must be written as its own file in `/qctests`, of the form `def test(p, parameters)`, where `p` is a profile object; each test returns a bool, where `True` indicates the test has *failed*.
`parameters` is a dictionary for conveniently persisting *static* parameters and sharing them between threads; if your test has a great deal of parameters to load before it runs, include alongside its definition a `loadParmaeters(dict)` method, which writes those
parameters to keys of your choosing on the dictionary passed in as an argument to `loadParameters`. That dictionary will subsequently be passed into every qc test as the `parameters` argument. Calling this `loadParameters` function is done automatically by the qc framework;
it is enough for you to just write it, and the parameters you want will be available in your qc test on the keys you defined on the `parameters` object.

###Testing Code
To run the code tests:

```
pip install nose
nosetests tests/*.py
```

##Profile Objects Specification
See [wodpy package](https://github.com/IQuOD/wodpy) for more information on the WodProfile class, a decoding helper for the WOD ASCII format.

##Contributing
Quality control checks waiting to be implemented are listed in the Issues. If you would like to work on coding up a check, please assign yourself to the issue to avoid others duplicating the effort.
If you have an idea for a new QC check, please open an issue and let us know, so we can help get you started on the right track.
