'''Test the loose_location_at_sea test is working as expected.'''

from util.testingProfile import fakeProfile
import numpy as np
import qctests.loose_location_at_sea as las

def test_data_halo():
    '''Check that the halo around the global relief data to handle obs
       next to the dateline is correct.
    '''

    assert np.array_equal(las.etoph[1000, 0:las.width*2], 
                          las.etoph[1000, -las.width*2:]), 'Data halo incorrect' 

def test_invalid_locations():
    '''Test that the check is able to handle invalid locations.'''

    p = fakeProfile([0], [0], latitude=-91, longitude=10)
    qc = las.test(p)
    assert np.all(qc), 'Latitude < -90 not handled correctly'

    p = fakeProfile([0], [0], latitude=91, longitude=10)
    qc = las.test(p)
    assert np.all(qc), 'Latitude > 90 not handled correctly'

    p = fakeProfile([0], [0], latitude=0, longitude=-181)
    qc = las.test(p)
    assert np.all(qc), 'Longitude < -180 not handled correctly'

    p = fakeProfile([0], [0], latitude=0, longitude=361)
    qc = las.test(p)
    assert np.all(qc), 'Longitude > 360 not handled correctly'

    p = fakeProfile([0], [0], latitude=0, longitude=-180)
    qc = las.test(p)
    assert np.all(qc == False), 'Latitude == -180 not handled correctly'
    
def test_ocean_point():
    '''Check that the test correctly handles an ocean point.'''

    p = fakeProfile([0], [0], latitude = 4.10566666667, longitude = -38.0133333333)
    qc = las.test(p)
    assert np.all(qc == False), 'Ocean point not handled correctly'

def test_land_point():
    '''Check that the test correctly handles a land point.'''

    p = fakeProfile([0], [0], latitude = -4.10566666667, longitude = -39)
    qc = las.test(p)
    assert np.all(qc == True), 'Land point not handled correctly'

def test_coast_point():
    '''Check that the test correctly handles a point right on the coast.'''

    p = fakeProfile([0], [0], latitude = -4.1, longitude = -38.15)
    qc = las.test(p)
    assert np.all(qc == False), 'Coast point not handled correctly'

