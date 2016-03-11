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
from xml.dom import minidom
import bmesh
import os
import sys
import bz2

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
    #TODO
    include_textures = BoolProperty(
        name="Include textures",
        description="Include texture data in the model file (not implemented)",
        default=False
    )
    
    compress = BoolProperty(
        name="Compress (bz2)",
        default=False
    )
    
    pretty_print = BoolProperty(
        name="XML Pretty print",
        default=True
    )

    def execute(self, context):
        self.context=context
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        model=context.active_object
        
        if self.triangulate:
            triangulate(model)
        
        shape = export(
            model=model,
            scale=self.scale,
            skip_materials = self.skip_materials,
            swap_yz = self.swap_yz,
        )
        
        if self.triangulate:
            bpy.ops.ed.undo()
        
        type = ET.SubElement(shape,"type")

        if self.animation:
            type.text="animation"
        else:
            type.text="static"
            
        tree = ET.ElementTree(shape)
       
        data = ET.tostring(tree.getroot())
        
        enc = None
        
        if self.pretty_print:
            data = minidom.parseString(data).toprettyxml(indent="\t")
            enc = 'utf8'
        
        if self.compress:
            f = open(self.filepath+".bz2","wb")    
            data = bytes(bz2.compress(data))
        else:
            f = open(self.filepath,"wb")
            
            if enc is None:
                 data = bytes(data) 
            else:
                 data = bytes(data, enc) 
           
        f.write(data)
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