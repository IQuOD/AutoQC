import util.AOMLinterpolation as AOMLinterpolation
import numpy

def closest_index_test():

	assert AOMLinterpolation.closest_index([10,11,12,13,14], 12.1) == 2, 'missed a slightly high point'
	assert AOMLinterpolation.closest_index([10,11,12,13,14], 11.9) == 2, 'missed a slightly low point'
	assert AOMLinterpolation.closest_index([10,11,12,13,14], 12) == 2, 'confused when point falls within list'
	assert AOMLinterpolation.closest_index([10,11,12,12,14], 12.1) == 2, 'if nearest number falls in list twice, should return the lower index'
	assert AOMLinterpolation.closest_index([12,10,11,13,14], 12.1) == 0, 'confused when nearest list part is at start of list'
	assert AOMLinterpolation.closest_index([10,11,13,14,12], 12.1) == 4, 'confused when nearest list part is at end of list'
	assert AOMLinterpolation.closest_index([10,11,12,13,14], 100) == 4, 'confused when point falls outside of list'
	assert AOMLinterpolation.closest_index([14,12,10,11,13], 12) == 1, 'confused when list out of order'

def get_index_and_next_test():
 
	assert AOMLinterpolation.get_index_and_next([10,11,12,13,14], 12.1) == (2,3), 'missed a simple bracket'
	assert AOMLinterpolation.get_index_and_next([10,11,12,13,14], 15) == (3,4), 'point outside range of list should return closest bracket'
	assert AOMLinterpolation.get_index_and_next([10,11,13,12,14], 12.1) == (3,4), '12.1 > list[3], so should return 3,4'
	assert AOMLinterpolation.get_index_and_next([10,11,13,12,10], 12.1) == (3,4), '12.1 > list[3], so should return 3,4 - even though 12.1 is outside the bracket'
	assert AOMLinterpolation.get_index_and_next([12,13,12,13], 12.1) == (0,1), 'with two equivalent choices, should take the bracket with lower indices'

def indices_without_nan_test():

	x = AOMLinterpolation.indices_without_nan(0, 1, [0,0,0,0,0], [[1,2],[2,3],[4,5],[6,7],[8,9]])
	assert numpy.array_equal(x, [0,1,2,3,4]), 'should return all indices with no pathological cases'

	x = AOMLinterpolation.indices_without_nan(0, 1, [0,0,0,0], [[1,2],[2,3],[4,5],[6,7],[8,9]])
	assert numpy.array_equal(x, [0,1,2,3]), 'indices should be constrained to the range of indices in the first list'

	x = AOMLinterpolation.indices_without_nan(0, 1, [0,0,0,0,0], [[1,2],[2,3],[4,5],[6,float('nan')],[8,9]])
	assert numpy.array_equal(x, [0,1,2,4]), 'nans in position v2[k][i] or v2[k][j] invalidate index k' 

	x = AOMLinterpolation.indices_without_nan(0, 1, [0,0,0,0,0], [[1,2],[2,3, float('nan')],[4,5],[6,7],[8,9]])
	assert numpy.array_equal(x, [0,1,2,3,4]), 'nans outside of v2[k][i] and v2[k][j] dont matter'	

	x = AOMLinterpolation.indices_without_nan(0, 2, [0,0,0,0,0], [[1,2,0],[2,3],[4,5,0],[6,7,0],[8,9,0]])
	assert numpy.array_equal(x, [0,2,3,4]), 'i or j out of range in v2[k] invalidate k'



