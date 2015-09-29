import data.ds as ds
import numpy

def test_readRegionCodes_spotcheck():
    '''
    check a few elements of the region codes.
    '''

    codes = ds.readRegionCodes()

    assert codes[0]  == None, 'code 0 should be None'
    assert codes[12] == 'South_Pacific', 'code 12 should be South_Pacific'
    assert codes[27] == 'Sulu_Sea', 'code 27 should be Sulu_Sea'

def test_readCellCodes_structure():
    '''
    make sure the cell codes table has the right structure:
    (lat, long) keys with int values.
    '''

    codes = ds.readCellCodes()

    for key in codes.keys():
        assert isinstance(key, tuple), 'found a key that is not a tuple'
        assert len(key) == 2, 'found a tuple key with wrong length (!=2)'
        assert isinstance(key[0], float), 'found a tuple with non-float first element'
        assert isinstance(key[1], float), 'found a tuple with non-float second element'
        assert isinstance(codes[key], int), 'all values in cell code dictionary must be ints'

def test_readWOD_temperature_ranges_structure():
    '''
    make sure the temperature range tble has the right structure:
    dict with region names for keys, values are objects with min and max keys
    and corresponding arrays of floats
    '''

    ranges = ds.readWOD_temperature_ranges()

    for key in ranges.keys():
        assert isinstance(key, str), 'all keys should be strings'
        if key == 'depths':
            assert isinstance(ranges[key], numpy.ndarray), 'depth key should contain an ndarray'
            for i in range(len(ranges[key])):
                assert isinstance(ranges[key][i], float), 'depth values should be floats'
        else:
            assert numpy.array_equal(ranges[key].keys(), ['max', 'min']), 'all regions should contain exactly two keys, min and max'
            assert isinstance(ranges[key]['max'], numpy.ndarray), 'maxima should be in an ndarray'
            assert isinstance(ranges[key]['min'], numpy.ndarray), 'minima should be in an ndarray'
            assert len(ranges[key]['min']) == len(ranges[key]['max']), 'minima and maxima arrays must be equal length'
            for i in range(len(ranges[key]['min'])):
                assert isinstance(ranges[key]['min'][i], float), 'minima should be floats'
                assert isinstance(ranges[key]['max'][i], float), 'maxima should be floats'

            