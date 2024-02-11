import util.obs_utils as outils
import numpy as np

def t48tot68_test():
    '''
    spotcheck on temperature conversion
    '''

    assert isinstance(outils.t48tot68(100), float), 'temperature conversion not returing a float'
    assert outils.t48tot68(100) == 100, 'temperature conversion not matching expectation at t48=100'

def t68tot90_test():
    '''
    Check the temperature differences between ITPS-68 and -90 reported in
    http://www.teos-10.org/pubs/gsw/pdf/t90_from_t48.pdf
    '''

    assert np.round( 10000*(outils.t68tot90(-10.0024) - -10.)) == 0, 'failed to match expectation at t90=-10'
    assert outils.t68tot90(0) == 0, 'failed to match expectation at t90=0'
    assert np.round( 10000*(outils.t68tot90(10.0024) - 10.)) == 0, 'failed to match expectation at t90=10' 
    assert np.round( 10000*(outils.t68tot90(20.0048) - 20.)) == 0, 'failed to match expectation at t90=20'
    assert np.round( 10000*(outils.t68tot90(30.0072) - 30.)) == 0, 'failed to match expectation at t90=30'
    assert np.round( 10000*(outils.t68tot90(40.0096) - 40.)) == 0, 'failed to match expectation at t90=40'  

def pottem_test():
    '''
    todo
    '''

    assert True

def depth_to_pressure_test():
    '''
    check behavior of depth_to_pressure for different input shapes.
    '''

    lat = 30.0
    depth = 10000
    truePressure = 1.0300976068e+10

    #two single value arrays
    assert np.round(1e6*outils.depth_to_pressure( np.array([depth]), np.array([lat]) )) == truePressure, 'failed to match expectation for 2 single-valued arrays'

    #single lat, array of depths
    p = outils.depth_to_pressure( np.array([depth, depth, depth]), np.array([lat]) )
    for i in range(len(p)):
        assert np.round(1e6*p[i]) == truePressure, 'failed to match expectation when given multiple depths and a single latitude.'

    #single depth, array of latitudes
    p = outils.depth_to_pressure( np.array([depth]), np.array([lat, lat, lat]) )
    for i in range(len(p)):
        assert np.round(1e6*p[i]) == truePressure, 'failed to match expectation when given multiple latitudes and a single depth.'

    #array of depths, array of latitudes
    p = outils.depth_to_pressure( np.array([depth, depth, depth]), np.array([lat, lat, lat]) )
    for i in range(len(p)):
        assert np.round(1e6*p[i]) == truePressure, 'failed to match expectation when given arrays of both latitude depth.'

def pressure_to_depth_test():
    '''
    implements the checkvalue suggested in the original implementation.
    '''

    # for scalars
    assert np.round(outils.pressure_to_depth(10000, 30.0)*1000) == 9713735

    # for numpy arrays
    depths = outils.pressure_to_depth(np.array([10000, 10000, 10000]), np.array([30.0, 30.0, 30.0]))
    for i in range(len(depths)):
        assert np.round(depths[i]*1000) == 9713735


def density_test():
    '''
    implements the checkvalue suggested in the original implementation.
    '''

    t = np.array([25.,20.,12.])
    s = np.array([35.,20.,40.])
    p = np.array([2000.,1000.,8000.])
    rhoTrue = np.array([1031.654229, 1017.726743, 1062.928258])

    # by arrays:
    rho = outils.density(t,s,p)
    for i in range(len(rho)):
        assert np.round(1e6*rho[i]) == np.round(1e6*rhoTrue[i]), 'failed to reconstruct density from array arguments'

    # by scalars:
    for i in range(len(t)):
        assert np.round(1e6*outils.density(t[i], s[i], p[i])) == np.round(1e6*rhoTrue[i]), 'failed to reconstruct density for scalar args'



