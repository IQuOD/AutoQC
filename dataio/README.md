## Data Unpacking

World Ocean Database data is encoded by the specification described [here](http://data.nodc.noaa.gov/woa/WOD/DOC/wodreadme.pdf). This `WodProfile` class reads this format, and returns an object with functions to help extract useful information from it.

### Usage

To use the `WodProfile` class, open a text file that conforms to the specification defined in the link above, and pass in the resulting file object:

```
fid = open("data/quota_subset.dat") 
profile = WodProfile(fid) # Reads a single profile.
```

`profile` now contains an object with many helper functions for extracting useful information:

```
profile.latitude()  # Return the latitude of the profile.
profile.z()         # Return the depths of the observations.
profile2 = WodProfile(fid) # Read the next profile.
profile2.is_last_profile_in_file() # Is this the last profile?
```

### `WodProfile` methods

These methods are intended for end-user use, for decoding useful information from a profile.

#### File Navigation

There may be many profiles in a single text file; these functions help walk around the collection of profiles found in the file.

 - `advance_file_position_to_next_profile(fid)`: Advance to the next profile in the current file `fid`.
 - `is_last_profile_in_file(fid)`: Returns true if this is the last profile in the data file `fid`.
 - `return_file_position_to_start_of_profile(fid)`: Return the file `fid` position to the start of the profile.

#### Data Retrieval

These functions decode data from the current profile.


 - `day()`: Returns the day.
 - `latitude()`: Returns the latitude of the profile.
 - `longitude()`: Returns the longitude of the profile.
 - `month()`: Returns the month.
 - `n_levels()`: Returns the number of levels in the profile.
 - `primary_header_keys()`: Returns a list of keys in the primary header.
 - `probe_type()`: Returns the contents of secondary header 29 if it exists, otherwise None.
 - `s()`: Returns a numpy masked array of salinity.
 - `s_level_qc(originator=False)`: Returns the quality control flag for each salinity level.
 - `s_profile_qc(originator=False)`: Returns the quality control flag for the salinity profile. 
 - `s_qc_mask()`: Returns a boolean array showing which salinity levels failed quality control. If the entire cast was rejected then all levels are set to True.
 - `t()`: Returns a numpy masked array of temperatures.
 - `t_level_qc(originator=False)`: Returns the quality control flag for each temperature level.
 - `t_profile_qc(originator=False)`: Returns the quality control flag for the temperature profile.
 - `t_qc_mask()`: Returns a boolean array showing which temperature levels failed quality control. If the entire cast was rejected then all levels are set to True.
 - `time()`: Returns the time.
 - `uid()`: Returns the unique identifier of the profile.
 - `var_data(index)`: Returns the data values for a variable given the variable index. 
 - `var_index(code=1, s=False)`: Returns the variable index for a variable. Either the variable code can be specified or s can be set to True to return the salinity index. Otherwise temperature index is returned.
 - `var_level_qc(index, originator=False)`: Returns the quality control codes for the levels in the profile.
 - `var_profile_qc(index, originator=False)`: Returns the quality control flag for entire cast.
 - `var_qc_mask(index)`: Returns a boolean array showing which levels are rejected by the quality control (values are True). A true is only put in the array if there is a rejection (not if there is a missing value).
 - `year()`: Returns the year. 
 - `z()`: Returns a numpy masked array of depths. 
 - `z_level_qc(originator=False)`: Returns a numpy masked array of depth quality control flags. Set the originator option if the originator flags are required.





 
 
 
 


 









