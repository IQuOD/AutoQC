#!/usr/bin/env python
import copy
import numpy as np
import os

class WodProfile(object):
    """ Main class to parse a WOD ASCII file

        Input:
            fid: File object of an open WOD ASCII file.

        Output:
            Each time this class is initialised it reads a 
            single profile from the input file. The data are
            parsed into a set of dictionaries and lists. 
            Functions are defined to extract some of the
            commonly used information from these.

        Example:
            fid = open("XBTO1966") 
            profile = WodProfile(fid) # Reads a single profile.
            profile.latitude()  # Return the latitude of the profile.
            profile.z()         # Return the depths of the observations.
            profile2 = WodProfile(fid) # Read the next profile.
            profile2.is_last_profile_in_file() # Is this the last profile?
            fid.close()
    """
    def __init__(self, fid, load_profile_data=True):

        # Record of where the profile occurs.
        self.file_name = fid.name
        self.file_position = fid.tell()
        
        # Record if CR+LF characters are being used at the end of lines.
        fid.seek(self.file_position + 80)
        char = fid.read(1)
        if char == '\r': 
            self.cr = True 
        else:
            self.cr = False
        fid.seek(self.file_position)

        # Read the various sections of the profile record.
        self._read_primary_header(fid)
        self._read_character_data_and_principal_investigator(fid)
        self._read_secondary_or_biological_header(fid)
        self._read_secondary_or_biological_header(fid, bio=True)
        if self.biological_header['Total bytes'] > 0:
            self._read_taxonomic_data(fid)
        else:
            self.taxa = {}
        if load_profile_data:
            self._read_profile_data(fid)
        else:
            self.profile_data = []

        # Wind forward to the next profile in the file.
        self.advance_file_position_to_next_profile(fid)

    # ROUTINES THAT READ AND INTERPRET INFORMATION FROM THE FILE
    def _read_chars(self, fid, nChars):
        # Read characters from the file. If the section
        # includes a line feed then an extra character
        # is read and the line feed is deleted. Has to cope
        # with files with Windows or Linux line endings.
        chars = fid.read(nChars)
        lfError = True
        while lfError:
            lfError = False
            for iChar, char in enumerate(chars):
                if char == '\r' or char == '\n':
                    iError = iChar
                    lfError = True
                    break
            if lfError: chars = chars[0:iError] + chars[iError+1:] + fid.read(1)
        return chars

    def _interpret_data(self, fid, format, dest):
        # This routine extracts the information from the ASCII file
        # using the formatting information supplied to it and 
        # stores the result in the dest dictionary.
        sigDigits = None
        precision = None

        for i, item in enumerate(format):
            if item[1] == 0: continue # Skip if not reading anything.

            chars = self._read_chars(fid, item[1])
 
            # Check if we need to skip the next few items.
            if item[0] == 'Significant digits' and chars == '-':
                format[i+1][1] = 0
                format[i+2][1] = 0
                dest[format[i+3][0]] = None
                continue

            # Cast to the required data type.
            value = item[2](chars)

            # Check for special items otherwise store the data
            # in the destination dictionary.
            if item[0] == 'Bytes in next field':
                format[i+1][1] = value
            elif item[0] == 'Significant digits':
                sigDigits = value
            elif item[0] == 'Total digits':
                format[i+2][1] = value
            elif item[0] == 'Precision':
                precision = value
            else:
                dest[item[0]] = value

            if item[0] != 'Precision' and precision is not None:
                dest[item[0]] /= 10**precision
                dest[item[0] + ' precision'] = precision
                dest[item[0] + ' significant digits'] = sigDigits
                sigDigits = None
                precision = None

        return None

    def _read_primary_header(self, fid):
        # Reads the primary header from the WOD ASCII profile.
        prhFormat = [['WOD Version identifier', 1, str],
                     ['Bytes in next field',    1, int],
                     ['Bytes in profile',       0, int],
                     ['Bytes in next field',    1, int],
                     ['WOD unique cast number', 0, int],
                     ['Country code',           2, str],
                     ['Bytes in next field',    1, int],
                     ['Cruise number',          0, int],
                     ['Year',                   4, int],
                     ['Month',                  2, int],
                     ['Day',                    2, int],
                     ['Significant digits',     1, int],
                     ['Total digits',           1, int],
                     ['Precision',              1, int],
                     ['Time',                   0, float],
                     ['Significant digits',     1, int],
                     ['Total digits',           1, int],
                     ['Precision',              1, int],
                     ['Latitude',               0, float],  
                     ['Significant digits',     1, int],
                     ['Total digits',           1, int],
                     ['Precision',              1, int],
                     ['Longitude',              0, float],
                     ['Bytes in next field',    1, int],
                     ['Number of levels',       0, int],
                     ['Profile type',           1, str],
                     ['Number of variables',    2, int]]  

        varFormat = [['Bytes in next field',    1, int],
                     ['Variable code',          0, int],
                     ['Quality control flag for variable', 1, int],
                     ['Bytes in next field',    1, int],
                     ['Number of variable-specific metadata', 0, int]]

        metFormat = [['Bytes in next field',    1, int],
                     ['Variable-specific code', 0, int],
                     ['Significant digits',     1, int],
                     ['Total digits',           1, int],
                     ['Precision',              1, int],
                     ['Value',                  0, float]]

        primary_header = {}

        self._interpret_data(fid, prhFormat, primary_header)
        # Now read variable specific metadata.
        primary_header['variables'] = []
        for iVar in range(primary_header['Number of variables']):
            primary_header['variables'] += [{}]
            self._interpret_data(fid, copy.deepcopy(varFormat), primary_header['variables'][iVar])
            primary_header['variables'][iVar]['metadata'] = []
            for iMetadata in range(primary_header['variables'][iVar]['Number of variable-specific metadata']):
                primary_header['variables'][iVar]['metadata'] += [{}]
                self._interpret_data(fid, copy.deepcopy(metFormat), primary_header['variables'][iVar]['metadata'][iMetadata])

        self.primary_header = primary_header
        return None

    def _read_character_data_and_principal_investigator(self, fid):
        # Reads the character data and principal investigator section
        # of the file.

        character_data_and_principal_investigator = {}

        charFormat1 = [['Bytes in next field',            1, int],
                       ['Total bytes',                    0, int]]
        charFormat2 = [['Number of entries',              1, int]]
        charFormat3 = [['Type of data',                   1, int]]
        charFormat4 = [['Bytes in next field',            2, int],
                       ['Character data',                 0, str]]
        charFormat5 = [['Number of PI names',             2, int]]
        charFormat6 = [['Bytes in next field',            1, int],
                       ['Variable code',                  0, int],
                       ['Bytes in next field',            1, int],
                       ['P.I. code',                      0, int]]

        self._interpret_data(fid, charFormat1, character_data_and_principal_investigator)
        if 'Total bytes' in character_data_and_principal_investigator:
            self._interpret_data(fid, charFormat2, character_data_and_principal_investigator)
            character_data_and_principal_investigator['entries'] = []
            for i in range(character_data_and_principal_investigator['Number of entries']):
                character_data_and_principal_investigator['entries'] += [{}]
                self._interpret_data(fid, charFormat3, character_data_and_principal_investigator['entries'][i])
                if character_data_and_principal_investigator['entries'][i]['Type of data'] < 3:
                    self._interpret_data(fid, copy.deepcopy(charFormat4), character_data_and_principal_investigator['entries'][i])
                else:
                    self._interpret_data(fid, copy.deepcopy(charFormat5), character_data_and_principal_investigator['entries'][i])
                    character_data_and_principal_investigator['entries'][i]['PIs'] = []
                    for j in range(character_data_and_principal_investigator['entries'][i]['Number of PI names']):
                        character_data_and_principal_investigator['entries'][i]['PIs'] += [{}]
                        self._interpret_data(fid, copy.deepcopy(charFormat6), character_data_and_principal_investigator['entries'][i]['PIs'][j])
        else:
            character_data_and_principal_investigator['Total bytes'] = 0
            character_data_and_principal_investigator['Number of entries'] = 0

        self.character_data_and_principal_investigator = character_data_and_principal_investigator
        return None

    def _read_secondary_or_biological_header(self, fid, bio=False):
        # Reads either the secondary header or the biological 
        # header. The format of the two are identical.

        header  = {}

        format1 = [['Bytes in next field',            1, int],
                   ['Total bytes',                    0, int]]
        format2 = [['Bytes in next field',            1, int],
                   ['Number of entries',              0, int]]
        format3 = [['Bytes in next field',            1, int],
                   ['Code',                           0, int],
                   ['Significant digits',             1, int],
                   ['Total digits',                   1, int],
                   ['Precision',                      1, int],
                   ['Value',                          0, float]]

        self._interpret_data(fid, format1, header)
        if 'Total bytes' in header:
            self._interpret_data(fid, format2, header)
            header['entries'] = []
            for i in range(header['Number of entries']):
                header['entries'] += [{}]
                self._interpret_data(fid, copy.deepcopy(format3), header['entries'][i])
        else:
            header['Total bytes'] = 0
            header['Number of entries'] = 0

        if bio:
            self.biological_header = header
        else:
            self.secondary_header  = header
        return None

    def _read_taxonomic_data(self, fid):
        # Placeholder for a reader for taxa data.
        taxa = {}
        format1 = [['Bytes in next field', 1, int],
                   ['Number of taxa sets', 0, int]]
        format2 = [['Bytes in next field', 1, int],
                   ['Number of entries',   0, int]]
        format3 = [['Bytes in next field', 1, int],
                   ['Code',                0, int],
                   ['Significant digits',  1, int],
                   ['Total digits',        1, int],
                   ['Precision',           1, int],
                   ['Value',               0, float],
                   ['Quality control flag', 1, int],
                   ['Originator flag',     1, int]]
        self._interpret_data(fid, format1, taxa)
        if 'Number of taxa sets' in taxa:
            taxa['sets'] = []
            for i in range(taxa['Number of taxa sets']):
                taxa['sets'] += [{}]
                self._interpret_data(fid, copy.deepcopy(format2), taxa['sets'][i])
                taxa['sets'][i]['entries'] = []
                for j in range(taxa['sets'][i]['Number of entries']):
                    taxa['sets'][i]['entries'] += [{}]
                    self._interpret_data(fid, copy.deepcopy(format3), taxa['sets'][i]['entries'][j])
        else:
            taxa['Number of taxa sets'] = 0
        self.taxa = taxa
        return None

    def _read_profile_data(self, fid):

        dFormat1 = [['Significant digits', 1, int],
                    ['Total digits',       1, int],
                    ['Precision',          1, int],
                    ['Depth',              0, float]]
        dFormat2 = [['Depth error code',   1, int],
                    ['Originator depth error flag', 1, int]]
        vFormat1 = [['Significant digits',  1, int],
                    ['Total digits',        1, int],
                    ['Precision',           1, int],
                    ['Value',               0, float]]
        vFormat2 = [['Value quality control flag', 1, int],
                    ['Value originator flag',      1, int]]

        data = []
        for i in range(self.primary_header['Number of levels']):
            data += [{}]
            self._interpret_data(fid, copy.deepcopy(dFormat1), data[i])
            if data[i]['Depth'] is not None:
                data[i]['Missing'] = False
            else:
                data[i]['Missing'] = True
                continue
            self._interpret_data(fid, copy.deepcopy(dFormat2), data[i])
            data[i]['variables'] = []
            for j in range(self.primary_header['Number of variables']):
                data[i]['variables'] += [{}]
                self._interpret_data(fid, copy.deepcopy(vFormat1), data[i]['variables'][j])
                if (data[i]['variables'][j]['Value'] is not None):
                    data[i]['variables'][j]['Missing'] = False
                    self._interpret_data(fid, copy.deepcopy(vFormat2), data[i]['variables'][j])
                else:
                    data[i]['variables'][j]['Missing'] = True

        self.profile_data = data
        return None

    # FILE POSITIONING
    def _calculate_next_profile_position(self):
        # Returns the file position of the next profile. 
        nLines = self.primary_header['Bytes in profile'] // 80
        if (self.primary_header['Bytes in profile'] % 80) > 0: nLines += 1
        if self.cr:
            mult = 82
        else:
            mult = 81
        return self.file_position + nLines * mult

    def advance_file_position_to_next_profile(self, fid):
        """ Advance to the next profile in the current file. """
        # Each profile record is made up of 80 data characters 
        # (including blanks at the end of the profile)
        # and return characters (LF+CR).
        fid.seek(self._calculate_next_profile_position())
        return None

    def return_file_position_to_start_of_profile(self, fid):
        """ Return the file position to the start of the profile. """
        fid.seek(self.file_position, 0)    
        return None

    def is_last_profile_in_file(self, fid):
        """ Returns true if this is the last profile in the data file. """
        return self._calculate_next_profile_position() == os.fstat(fid.fileno()).st_size

    # CONVENIENCE FUNCTIONS FOR RETRIEVAL OF INFORMATION FROM A PROFILE
    def primary_header_keys(self):
        """ Returns a list of keys in the primary header. """
        return [d for d in self.primary_header]

    def latitude(self):
        """ Returns the latitude of the profile. """
        return self.primary_header['Latitude']

    def longitude(self):
        """ Returns the longitude of the profile. """
        return self.primary_header['Longitude']

    def uid(self):
        """ Returns the unique identifier of the profile. """
        return self.primary_header['WOD unique cast number']

    def n_levels(self):
        """ Returns the number of levels in the profile. """
        return self.primary_header['Number of levels']

    def year(self):
        """ Returns the year. """
        return self.primary_header['Year']

    def month(self):
        """ Returns the month. """
        return self.primary_header['Month']

    def day(self):
        """ Returns the day. """
        return self.primary_header['Day']

    def time(self):
        """ Returns the time. """
        return self.primary_header['Time']
        
    def probe_type(self):
        """ Returns the contents of secondary header 29 if it exists,
            otherwise None. """
        pt = None
        for item in self.secondary_header['entries']:
            if item['Code'] == 29:
                pt = item['Value']
        return pt

    def z(self):
        """ Returns a numpy masked array of depths. """
        data = np.ma.array(np.zeros(self.n_levels()), mask=True)
        for i in range(self.n_levels()):
            if self.profile_data[i]['Missing']: continue
            data[i] = self.profile_data[i]['Depth']
        return data

    def z_level_qc(self, originator=False):
        """ Returns a numpy masked array of depth 
            quality control flags. Set the originator
            option if the originator flags are required. """
        data = np.ma.array(np.zeros(self.n_levels()), mask=True, dtype=int)
        for i in range(self.n_levels()):
            if self.profile_data[i]['Missing']: continue
            if originator:
                data[i] = self.profile_data[i]['Originator depth error flag']
            else:
                data[i] = self.profile_data[i]['Depth error code']
        return data        

    def var_index(self, code=1, s=False):
        """ Returns the variable index for a variable. 
            Either the variable code can be specified
            or s can be set to True to return the salinity
            index. Otherwise temperature index is returned."""
        if s:
            code = 2

        index = None
        for i, var in enumerate(self.primary_header['variables']):
            if var['Variable code'] == code:
                assert index is None, 'Appears to be two sets of same data in profile'
                index = i
        return index

    def var_data(self, index):
        """ Returns the data values for a variable given the variable index. """
        data = np.ma.array(np.zeros(self.n_levels()), mask=True)
        if index is not None:
            for i in range(self.n_levels()):
                if self.profile_data[i]['variables'][index]['Missing']: continue
                data[i] = self.profile_data[i]['variables'][index]['Value']
        return data

    def var_level_qc(self, index, originator=False):
        """ Returns the quality control codes for the levels in the profile. """
        data = np.ma.array(np.zeros(self.n_levels()), mask=True, dtype=int)
        if index is not None:
            for i in range(self.n_levels()):
                if self.profile_data[i]['variables'][index]['Missing']: continue
                if originator:
                    data[i] = self.profile_data[i]['variables'][index]['Value originator flag']
                else:
                    data[i] = self.profile_data[i]['variables'][index]['Value quality control flag']
        return data

    def var_profile_qc(self, index, originator=False):
        """ Returns the quality control flag for entire cast. """
        if index is None: return None
        if originator:
            return None # There is no originator flag for the entire profile.
        else:
            return self.primary_header['variables'][index]['Quality control flag for variable']

    def var_qc_mask(self, index):
        """ Returns a boolean array showing which levels are rejected
            by the quality control (values are True). A true is only
            put in the array if there is a rejection (not if there is 
            a missing value)."""
        data = np.ma.array(np.zeros(self.n_levels()), mask=False, dtype=bool)
        prof = self.var_profile_qc(index)
        if prof > 0:
            data[:] = True
        else:
            zqc = self.z_level_qc()
            data[(zqc.mask == False) & (zqc > 0)] = True
            lqc = self.var_level_qc(index)
            data[(lqc.mask == False) & (lqc > 0)] = True
        return data

    def t(self):
        """ Returns a numpy masked array of temperatures. """
        index = self.var_index()
        return self.var_data(index)

    def t_qc_mask(self):
        """ Returns a boolean array showing which temperature
            levels failed quality control. If the entire cast
            was rejected then all levels are set to True."""
        index = self.var_index()
        return self.var_qc_mask(index)

    def t_level_qc(self, originator=False):
        """ Returns the quality control flag for each temperature level. """
        index = self.var_index()
        return self.var_level_qc(index, originator=originator)

    def s_qc_mask(self):
        """ Returns a boolean array showing which salinity
            levels failed quality control. If the entire cast
            was rejected then all levels are set to True."""
        index = self.var_index(s=True)
        return self.var_qc_mask(index)

    def t_profile_qc(self, originator=False):
        """ Returns the quality control flag for the temperature profile. """
        index = self.var_index()
        return self.var_profile_qc(index, originator=originator)

    def s(self):
        """ Returns a numpy masked array of salinity. """
        index = self.var_index(s=True)
        return self.var_data(index)

    def s_level_qc(self, originator=False):
        """ Returns the quality control flag for each salinity level. """
        index = self.var_index(s=True)
        return self.var_level_qc(index, originator=originator)

    def s_profile_qc(self, originator=False):
        """ Returns the quality control flag for the salinity profile. """
        index = self.var_index(s=True)
        return self.var_profile_qc(index, originator=originator)    



