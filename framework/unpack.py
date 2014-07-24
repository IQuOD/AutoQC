#!/usr/bin/env python
import os

dir = os.path.dirname(__file__)
datafile = os.path.join(dir, '../data/XBTO1966')
f = open(datafile)
text = f.readlines()
f.close()


class XBT(object):
    """ Main class to parse the XBT NOAA file

        Input:
            raw_text [String]: The full content of the XBT file.

        Output:
            This class responds as it was a dictionary of variables
            (See: http://data.nodc.noaa.gov/woa/WOD/DOC/wodreadme.pdf
            table 10.1)

        Ex.:
            f = open("XBTO1966")
            text = f.readlines()
            profile = XBT(text)
            profile.keys()  # Return the available variables
            profile['year'] # Return the year
            profile['variables'] # Return the variables
            profile.attributes # Return a dictionary with the file header
    """
    def __init__(self, raw_text):
        keys = ['WOD Version identifier', 'version', 'uniqueCast',
                'countryCode', 'cruiseNumber', 'year', 'month', 'day', 'time',
                'latitude', 'longitude', 'nDepths', 'profileType', 'variables']
        self.raw_text = raw_text
        self.attributes = dict.fromkeys(keys)

    def keys(self):
        return [d for d in self.attributes]

profile = XBT(text)
print profile.keys()
