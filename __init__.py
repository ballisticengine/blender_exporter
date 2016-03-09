# -*- coding: utf-8 -*-

bl_info = {
    "name": "XML Geometry format",
    "author": "Maciej Zakrzewski",
    "blender": (2, 57, 0),
    "location": "File > Import-Export",
    "description": "Export to xml format",
    "warning": "",
    "category": "Import-Export2"}



import bpy
from bpy.props import StringProperty, FloatProperty, BoolProperty, EnumProperty
from bpy_extras.io_utils import ImportHelper,ExportHelper,axis_conversion
from bpy.app.handlers import persistent
import bmesh

import os
import sys

@persistent
def setPath():
    sys.path.append(os.path.dirname(__file__))

setPath()

import xml.etree.ElementTree as ET
import math
from helper import *
from shape_export import *
from bounding_hepler import *
import imp

if "helper" in locals():
        imp.reload(helper)

if "shape_export" in locals():
    imp.reload(shape_export)

if "bounding_hepler" in locals():
    imp.reload(bounding_hepler)


class ExportXMLModel(bpy.types.Operator,ExportHelper):
    bl_idname = "export_scene.xml_model"
    bl_label = 'Export to XML Model'
    filename_ext = ".xml"
    scale = FloatProperty(
            name="Scale",
            description="",
            min=0.0, max=1000.0,
            default=1.0,
            )
    animation = BoolProperty(name="Animated", default=False)
    triangulate = BoolProperty(name="Triangulate", default=True)
    swap_yz = BoolProperty(name="Swap YZ axes", default=True)
    skip_materials = BoolProperty(
        name="Skip materials", 
        description="Don't export materials and textures",
        default=False
    )

    def execute(self, context):
        self.context=context
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        shape = export(
            model=context.active_object,
            scale=self.scale,
            skip_materials = self.skip_materials,
            triangulate = self.triangulate,
            swap_yz = self.swap_yz
        )
        type = ET.SubElement(shape,"type")

        if self.animation:
            type.text="animation"
        else:
            type.text="static"
            
        tree = ET.ElementTree(shape)
        f=open(self.filepath,"wb")
        print (self.filepath)
        tree.write(f)
        f.close()
        return {'FINISHED'}



def menu_func_export(self, context):
    self.layout.operator(ExportXMLModel.bl_idname, text="XML Model (.xml)")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()