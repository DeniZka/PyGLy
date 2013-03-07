"""Demonstrate's PyGLy's texture loading algorithms.
Loads textures from examples/data/textures/*
(assuming they have an accepted extension) and
renders them to a Quad.
Left and Right arrows switch textures.
"""
import os
import math
from time import time

from PIL import Image
import numpy
import pyglet

# disable the shadow window
# this uses a legacy profile and causes issues
# on OS-X
pyglet.options['shadow_window'] = False

from pyglet.gl import *

import pygly.viewport
from pygly.scene_node import SceneNode
from pygly.camera_node import CameraNode
from pygly.orthogonal_view_matrix import OrthogonalViewMatrix
import pygly.texture
from pygly.texture import Texture2D
import pygly.pil_texture
from pyrr import matrix44

from application import Application
from demo_simple import SimpleApplication
import quad


class TextureApplication( SimpleApplication ):

    def setup_viewports( self ):
        super( TextureApplication, self ).setup_viewports()

        # change our clear colour
        self.colours[ 0 ] = ( 0.5, 0.5, 0.5, 1.0 )

    def setup_scene( self ):
        """Creates the scene to be rendered.
        Creates our camera, scene graph, 
        """
        Application.setup_scene( self )

        # register our key press listener
        self.window.push_handlers(
            on_key_press = self.on_key_press
            )

        # setup our GL state
        # enable z buffer
        glEnable( GL_DEPTH_TEST )

        # enable back face culling
        glEnable( GL_CULL_FACE )
        glCullFace( GL_BACK )

        # enable alpha blending
        glEnable( GL_BLEND )
        glBlendFunc(
            GL_ONE,
            GL_ONE_MINUS_SRC_ALPHA
            )

        # create our cube renderable
        quad.create()

        # create our quad
        self.node = SceneNode( 'quad' )
        self.scene_node.add_child( self.node )

        # the quad is from -1:+1, so scale down to -0.5:+0.5
        self.node.world_transform.scale = [0.5, 0.5, 0.5]

        self.load_textures()

    def load_textures( self ):
        # load our textures
        self.textures = []
        self.current_texture = 0

        # find the textures relative to our module directory
        path = os.path.join(
            os.path.dirname( __file__ ),
            '../data/textures'
            )
        self.load_texture_directory( path )
        self.load_array_textures()
        self.print_texture_name()

    def load_texture_directory( self, directory ):
        print 'Loading images from', directory

        extensions = [
            '.png',
            '.jpg',
            '.jpeg',
            '.tif',
            '.bmp',
            '.exr',
            ]

        for filename in os.listdir( directory ):
            name, extension = os.path.splitext( filename )
            if extension not in extensions:
                continue

            try:
                print filename,
                full_path = '%s/%s' % (directory, filename)

                image = Image.open( full_path )
                print image.format, image.mode, image.getbands()

                texture = Texture2D()
                texture.bind()
                texture.set_min_mag_filter(
                    GL_NEAREST,
                    GL_NEAREST
                    )
                pygly.pil_texture.set_pil_image( texture, image )
                texture.unbind()

                self.textures.append( (filename, texture) )
            except IOError as e:
                print 'Exception:', e
                # ensure we unbound our textures
                glBindTexture( GL_TEXTURE_2D, 0 )

    def load_array_textures( self ):
        # create a random RGB texture
        name = 'Red Shade RGB'
        format = 'u8/rgb/rgb8'
        print name, format
        data = numpy.linspace( 0, 255, 32 * 32 * 3 )
        data.shape = (-1,3)
        data[:,1:3] = 0.0
        texture = Texture2D()
        texture.bind()
        texture.set_min_mag_filter( GL_NEAREST, GL_NEAREST )
        texture.set_image(
            data.astype('uint8').flat,
            (32,32),
            format
            )
        texture.unbind()
        self.textures.append( (name, texture) )

        # create a random luminance texture
        name = 'Random Luminance'
        format = 'u8/r/rgba8/rrr1'
        print name, format
        data = numpy.random.random_integers( 120, 255, 32 * 32 )
        texture = Texture2D()
        texture.bind()
        texture.set_min_mag_filter( GL_NEAREST, GL_NEAREST )
        texture.set_image(
            data.astype('uint8').flat,
            (32,32),
            format
            )
        texture.unbind()
        self.textures.append( (name, texture) )

    def setup_cameras( self ):
        # over-ride SimpleApplication's camera
        Application.setup_cameras( self )

        # change our view matrix to an orthogonal one
        self.cameras[ 0 ].view_matrix = OrthogonalViewMatrix(
            pygly.viewport.aspect_ratio( self.viewports[ 0 ] ),
            scale = [1.0, 1.0],
            near_clip = 1.0,
            far_clip = 200.0
            )

        # move the camera so we're not inside
        # the root scene node's debug cube
        self.cameras[ 0 ].transform.object.translate(
            [ 0.0, 0.0, 35.0 ]
            )
    
    def step( self, dt ):
        """Updates our scene and triggers the on_draw event.
        This is scheduled in our __init__ method and
        called periodically by pyglet's event callbacks.
        We need to manually call 'on_draw' as we patched
        it our of pyglets event loop when we patched it
        out with pygly.monkey_patch.
        Because we called 'on_draw', we also need to
        perform the buffer flip at the end.
        """
        Application.step( self, dt )

    def on_key_press( self, symbol, modifiers ):
        # change textures
        if symbol == pyglet.window.key.LEFT:
            self.current_texture -= 1
            if self.current_texture < 0:
                self.current_texture = len(self.textures) - 1
            self.print_texture_name()
        elif symbol == pyglet.window.key.RIGHT:
            self.current_texture += 1
            if self.current_texture >= len(self.textures):
                self.current_texture = 0
            self.print_texture_name()

    def print_texture_name( self ):
        print 'Current texture:', self.textures[ self.current_texture ][ 0 ]

    def render_scene( self, camera ):
        """Renders each renderable in the scene
        using the current projection and model
        view matrix.
        The original GL state will be restored
        upon leaving this function.
        """
        projection = camera.view_matrix.matrix
        model_view = camera.model_view

        # calculate a new model view
        world_matrix = self.node.world_transform.matrix
        current_mv = matrix44.multiply(
            world_matrix,
            model_view
            )

        # bind our texture
        glActiveTexture( GL_TEXTURE0 )
        texture = self.textures[ self.current_texture ][ 1 ]
        texture.bind()

        # render a cube
        quad.draw( projection, current_mv )

        texture.unbind()
    

def main():
    """Main function entry point.
    Simple creates the Application and
    calls 'run'.
    Also ensures the window is closed at the end.
    """
    # create app
    app = TextureApplication()
    app.run()
    app.window.close()


if __name__ == "__main__":
    main()

