'''
Created on 11/04/2012

@author: adam
'''

import math

import numpy


def zero( out = None, data_type = numpy.float ):
    if out == None:
        out = numpy.empty( (2,2), dtype = data_type )
    
    out[:] = [ [0.0, 0.0], [0.0, 0.0] ]
    return out

def create_from_bounds( left, right, bottom, top, out = None, data_type = numpy.float ):
    if out == None:
        out = numpy.empty( (2,2), dtype = data_type )

    out[:] = [
        [ left, bottom ],
        [ right - left, top - bottom ]
        ]
    return out

def extract_extents( rect ):
    left = min(
        rect[ (0, 0) ],
        rect[ (0, 0) ] + rect[ (1, 0) ]
        )
    right = max(
        rect[ (0, 0) ],
        rect[ (0, 0) ] + rect[ (1, 0) ]
        )
    bottom = min(
        rect[ (0, 1) ],
        rect[ (0, 1) ] + rect[ (1, 1) ]
        )
    top = max(
        rect[ (0, 1) ],
        rect[ (0, 1) ] + rect[ (1, 1) ]
        )
    return left, right, bottom, top

def is_point_within_rect( point, rect ):
    left, right, bottom, top = extract_extents( rect )
    if \
        point[ 0 ] < left or \
        point[ 0 ] > right or \
        point[ 1 ] < bottom or \
        point[ 1 ] > top:
        return False
    return True

def is_relative_point_within_rect( point, rect ):
    """
    Checks a point that is relative to a rect
    is within the rect itself.
    This is done by checking the point is < width
    and height.
    """
    left, right, bottom, top = extract_extents( rect )
    if \
        point[ 0 ] > (right - left) or \
        point[ 0 ] < 0 or \
        point[ 1 ] > (top - bottom) or \
        point[ 1 ] < 0:
        return False
    return True

def make_point_relative( point, rect ):
    """
    Takes an absolute point and makes it
    relative to a rect by subtracting
    the rect's x,y.
    This is the opposite of make_point_absolute.
    """
    left, right, bottom, top = extract_extents( rect )
    return [
        point[ 0 ] - left,
        point[ 1 ] - bottom
        ]

def make_point_absolute( point, rect ):
    """
    Takes a point that is relative to a rect
    and adds the rect's x,y to it to make it
    absolute. This is the opposite of
    make_point_relative.
    """
    left, right, bottom, top = extract_extents( rect )
    return [
        point[ 0 ] + left,
        point[ 1 ] + bottom
        ]

def scale_by_vector( rect, vec ):
    """
    Scales a rectangle by a 2D vector

    @param rect: the rectangle to scale.
    Both x,y and width,height will be scaled.
    The value will NOT be scaled in place.
    @param vec: A 2D vector to scale the rect
    by.
    @return Returns the rect scaled by vec.
    """
    if rect.shape != (2,2):
        raise ValueError( "Rect must be shape (2,2)" )
    if len(vec) != 2:
        raise ValueError( "Vec must be length 2" )
    return rect * vec


if __name__ == '__main__':
    rect = zero()
    rect[ 0 ] = [ 5.0, 5.0 ]
    rect[ 1 ] = [ 10.0, 10.0 ]

    assert False == is_point_within_rect( [ -1.0, 7.0 ], rect )
    assert True == is_point_within_rect( [ 5.0, 5.0 ], rect )
    assert False == is_point_within_rect( [ 20.0, 20.0 ], rect )

    rect[ 0 ] = [ 15.0, 15.0 ]
    rect[ 1 ] = [ -10.0, -10.0 ]
    assert False == is_point_within_rect( [ -1.0, 7.0 ], rect )
    assert True == is_point_within_rect( [ 5.0, 5.0 ], rect )
    assert False == is_point_within_rect( [ 20.0, 20.0 ], rect )

    rect[ 0 ] = [ 1.0, 1.0 ]
    rect[ 1 ] = [ 10.0, 1.0 ]
    scaled_rect = scale_by_vector( rect, [ 2.0, 1.0 ] )
    assert scaled_rect[ (0, 0) ] == 2.0
    assert scaled_rect[ (0, 1) ] == 1.0
    assert scaled_rect[ (1, 0) ] == 20.0
    assert scaled_rect[ (1, 1) ] == 1.0

