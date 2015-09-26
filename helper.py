import bpy
from bpy.props import StringProperty, FloatProperty, BoolProperty, EnumProperty
from bpy_extras.io_utils import (ImportHelper,
                                 ExportHelper,
                                 axis_conversion,
                                 )


import xml.etree.ElementTree as ET
import math


def makeRGBNode(parent):
    r=ET.SubElement(parent,'r')
    g=ET.SubElement(parent,'g')
    b=ET.SubElement(parent,'b')
    return (r,g,b)


def makeXYZode(parent):
    x=ET.SubElement(parent,'x')
    y=ET.SubElement(parent,'y')
    z=ET.SubElement(parent,'z')
    return (x,y,z)


def frame_to_time(frame_number):
    scene = bpy.context.scene
    fps = scene.render.fps
    fps_base = scene.render.fps_base
    raw_time = (frame_number - 1) / fps
    return raw_time


class EmptyUV:
    uv = (0.0, 0.0)
    def __getitem__(self, index): return self