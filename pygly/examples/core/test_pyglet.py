from OpenGL.GL import *

import numpy
import pyglet

# disable the shadow window
# this uses a legacy profile and causes issues
# on OS-X
pyglet.options['shadow_window'] = False

# patch pyglet's OpenGL legacy code out
import pyglet.window
def _on_resize( self, width, height ):
    # don't do anything
    pass

def _draw_mouse_cursor( self ):
    # don't do anything
    pass

def patch_window():
    # patch out any pyglet functions using
    # opengl legacy calls
    pyglet.window.BaseWindow.on_resize = _on_resize
    pyglet.window.BaseWindow.draw_mouse_cursor = _draw_mouse_cursor



vs_source = """
#version 150 core

in vec3 in_position;

out vec3 ex_position;

void main(void) 
{
    gl_Position = vec4( in_position, 1.0 );

    ex_position = in_position;
}
"""

fs_source = """
#version 150 core

in vec3 ex_position;

out vec4 out_frag_color;

void main(void) 
{
    out_frag_color = vec4( 0.0, 1.0, 0.0, 1.0 );
}
"""


gl_config = pyglet.gl.Config(
    depth_size = 24,
    double_buffer = True,
    major_version = 3,
    minor_version = 2,
    forward_compatible = True,
    )

window = pyglet.window.Window(
    fullscreen = False,
    width = 1024,
    height = 768,
    resizable = False,
    vsync = False,
    config = gl_config,
    )

glEnable( GL_SCISSOR_TEST )
glDisable( GL_CULL_FACE )
glDisable( GL_DEPTH_TEST )

# create a shader
vs = glCreateShader( GL_VERTEX_SHADER )
glShaderSource( vs, vs_source )
glCompileShader( vs )

fs = glCreateShader( GL_FRAGMENT_SHADER )
glShaderSource( fs, fs_source )
glCompileShader( fs )

shader = glCreateProgram()
glAttachShader( shader, vs )
glAttachShader( shader, fs )

# attribute values
glBindAttribLocation( shader, 0, "in_position" )
glBindFragDataLocation( shader, 0, "out_frag_color" )

glLinkProgram( shader )

if not glGetProgramiv( shader, GL_LINK_STATUS ):
    print glGetProgramInfoLog( shader )
    exit()

# create a triangle
vertices = numpy.array(
    [
         0.0, 0.8,-1.0,
        -0.8,-0.8,-1.0,
         0.8,-0.8,-1.0
        ],
    dtype = 'float32'
    )

#vertices *= 100.0

vao = glGenVertexArrays( 1 )
vbo = glGenBuffers( 1 )

glBindVertexArray( vao )

glBindBuffer( GL_ARRAY_BUFFER, vbo )
glBufferData(
    GL_ARRAY_BUFFER,
    vertices.nbytes,
    vertices,
    GL_STATIC_DRAW
    )
glVertexAttribPointer( 0, 3, GL_FLOAT, GL_FALSE, 0, 0 )
glEnableVertexAttribArray( 0 )

glBindBuffer( GL_ARRAY_BUFFER, 0 )
glBindVertexArray( 0 )


@window.event
def on_draw():
    global window
    global shader
    global vao
    global vertices

    glViewport(0, 0, window.width, window.height)

    glScissor( 0, 0, window.width, window.height )
    glClearColor( 0.5, 0.5, 0.5, 1.0 )
    glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

    glScissor( 0, 0, window.width / 2, window.height / 2 )
    glClearColor( 0.0, 0.0, 0.0, 1.0 )
    glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

    glScissor( 0, 0, window.width, window.height )

    glUseProgram( shader )
    glBindVertexArray( vao )

    glDrawArrays( GL_TRIANGLES, 0, vertices.size / 3 )

    glBindVertexArray( 0 )
    glUseProgram( 0 )

    glFlush()
    assert GL_NO_ERROR == glGetError()


pyglet.app.run()

