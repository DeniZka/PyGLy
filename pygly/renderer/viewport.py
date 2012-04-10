'''
Created on 20/06/2011

@author: adam
'''

import weakref

import numpy
from pyglet.gl import *

import maths.rect


class Viewport( object ):
    
    
    def __init__( self, rect ):
        """
        Creates a viewport with the size of rect.

        @param rect: An array with the shape (2,2).
        Values are from 0.0 -> 1.0.
        Values may exceed this but will be off the screen.
        A rect of [ [0.0,0.0],[1.0,1.0] ] is the equivalent
        of a whole window.
        """
        super( Viewport, self ).__init__()

        self.camera = None
        self.scene_node = None
        self.viewport_ratio = numpy.array(
            rect,
            dtype = numpy.float
            )

        if self.viewport_ratio.shape != (2,2):
            raise ValueError(
                "Viewport rect must be numpy array with shape (2,2)"
                )

    def set_camera( self, scene_node, camera ):
        self.scene_node = scene_node
        self.camera = weakref.ref( camera )
    
    def switch_to( self, window ):
        # update our viewport size
        pixel_rect = self.pixel_rect( window )
        glViewport(
            int(pixel_rect[ (0,0) ]),
            int(pixel_rect[ (0,1) ]),
            int(pixel_rect[ (1,0) ]),
            int(pixel_rect[ (1,1) ])
            )

    def aspect_ratio( self, window ):
        """
        Returns the aspect ratio of the viewport.

        Aspect ratio is the ratio of width to height
        a value of 2.0 means width is 2*height
        """
        pixel_rect = self.pixel_rect( window )
        aspect_ratio = float(pixel_rect[ (1,0) ]) / float(pixel_rect[ (1,1) ])
        return aspect_ratio

    def clear(
        self,
        window,
        values = GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT
        ):
        # clear the region
        # we use glScissor to set the pixels
        # we want to affect
        glEnable( GL_SCISSOR_TEST )

        pixel_rect = self.pixel_rect( window )
        glScissor( 
            int(pixel_rect[ (0,0) ]),
            int(pixel_rect[ (0,1) ]),
            int(pixel_rect[ (1,0) ]),
            int(pixel_rect[ (1,1) ])
            )
        # clear the background or we will just draw
        # ontop of other viewports
        glClear( values )

        glDisable( GL_SCISSOR_TEST )
    
    def push_view_matrix( self, window ):
        # the camera is a weak pointer
        # so we need to get a reference to it
        if self.camera != None:
            # apply our projection matrix
            self.camera().view_matrix.push_view_matrix(
                window,
                self
                )

    def pop_view_matrix( self ):
        # the camera is a weak pointer
        # so we need to get a reference to it
        if self.camera != None:
            # unapply our projection matrix
            self.camera().view_matrix.pop_view_matrix()
        
    def push_model_view( self ):
        # the camera is a weak pointer
        # so we need to get a reference to it
        if self.camera != None:
            # apply the camera's model view
            self.camera().push_model_view()

    def pop_model_view( self ):
        # the camera is a weak pointer
        # so we need to get a reference to it
        if self.camera != None:
            # unapply the camera's model view
            self.camera().pop_model_view()

    def render( self, window ):
        # render the current scene
        if self.scene_node != None:
            self.scene_node.render()

    def push_viewport_attributes( self ):
        glPushAttrib( GL_ALL_ATTRIB_BITS )
        self.setup_viewport()

    def pop_viewport_attributes( self ):
        glPopAttrib()

    def setup_viewport( self ):
        """
        Over-ride this method to customise
        the opengl settings for this viewport.

        The default method sets the following:
        -glEnable( GL_DEPTH_TEST )
        -glShadeModel( GL_SMOOTH )
        """
        # enable some default options
        # use the z-buffer when drawing
        glEnable( GL_DEPTH_TEST )

        # enable smooth shading
        glShadeModel( GL_SMOOTH )

        # because we use glScale for scene graph
        # scaling, normals will get affected too.
        # GL_RESCALE_NORMAL applies the inverse
        # value of the current matrice's scale
        # this is new in OGL1.2 and SHOULD be
        # faster than glEnable( GL_NORMALIZE )
        # http://www.opengl.org/archives/resources/features/KilgardTechniques/oglpitfall/
        glEnable( GL_RESCALE_NORMAL )

    def relative_point_to_ray( self, window, point ):
        """
        Returns a ray cast from 2d window co-ordinates
        into the world.

        @param viewport: The viewport being used to cast the ray.
        @param point: The 2D point, relative to this camera,
        to project a ray from. A list of 2 float values.
        @returns A ray consisting of 2 vectors (shape = 2,3).
        """
        # check that the point resides within the viewport
        pixel_rect = self.pixel_rect( window )
        if maths.rect.is_relative_point_within_rect( point, pixel_rect ):
            # tell our camera to cast the ray
            if self.camera != None:
                return self.camera().point_to_ray( window, self, point )
        else:
            raise ValueError( "Point does not lie within viewport" )

    def point_relative_to_viewport( self, window, point ):
        # convert to viewport co-ordinates
        pixel_rect = self.pixel_rect( window )
        return maths.rect.make_point_relative(
            point,
            pixel_rect
            )

    def is_point_within_viewport( self, window, point ):
        pixel_rect = self.pixel_rect( window )
        return maths.rect.is_point_within_rect(
            point,
            pixel_rect
            )

    def pixel_rect( self, window ):
        return maths.rect.scale_by_vector(
            self.viewport_ratio,
            [ window.width, window.height ]
            )

    @property
    def ratio_x( self ):
        return self.viewport_ratio[ (0,0) ]

    @property
    def ratio_y( self ):
        return self.viewport_ratio[ (0,1) ]
    
    @property
    def ratio_width( self ):
        return self.viewport_ratio[ (1,0) ]
    
    @property
    def ratio_height( self ):
        return self.viewport_ratio[ (1,1) ]


if __name__ == '__main__':
    window = pyglet.window.Window(
        fullscreen = False,
        width = 1024,
        height = 512
        )
    viewport = Viewport( [0.0, 0.0, 1.0, 1.0] )
    assert viewport.ratio_x == 0.0
    assert viewport.ratio_y == 0.0
    assert viewport.ratio_width == 1.0
    assert viewport.ratio_height == 1.0

    assert viewport.aspect_ratio( window ) == 2.0

    pixel_rect = viewport.pixel_rect( window )
    assert pixel_rect[ (0,0) ] == 0
    assert pixel_rect[ (0,1) ] == 0
    assert pixel_rect[ (1,0) ] == 1024
    assert pixel_rect[ (1,1) ] == 512

