import bpy
from bpy.props import StringProperty, FloatProperty, BoolProperty, EnumProperty
from bpy_extras.io_utils import (ImportHelper,
                                 ExportHelper,
                                 axis_conversion,
                                 )


import bmesh

import xml.etree.ElementTree as ET
import math

from helper import *

#TODO: remove redundant UV info (both face vertex and uv list)

def export(model, scale=1, skip_materials=False, swap_yz=False):
        loc=model.location.copy()
        shape = ET.Element('shape')
        name = ET.SubElement(shape,'name')
        loce = ET.SubElement(shape,"loc")
        lx,ly,lz = makeXYZode(loce)
        lx.text = str(loc.x)
        ly.text = str(loc.y)
        lz.text = str(loc.z)
        geom = ET.SubElement(shape,'geom')

        x_faces = ET.SubElement(geom,'faces')
        x_verts = ET.SubElement(geom,'vertices')
        x_uvs = ET.SubElement(geom,'uvs')
        
        uv_index=0
        name.text = model.data.name
        scene = bpy.context.scene
        oldmodel=None
  
        model=model.to_mesh(scene, True, 'PREVIEW')
        verts = model.vertices

        for v in verts:
            x_vertex = ET.SubElement(x_verts,'vertex')
            x_co = ET.SubElement(x_vertex,"coords")
            x_normal = ET.SubElement(x_vertex,'normal')
            x, y, z = makeXYZode(x_co)
            x.text = str(v.co[0]*scale)
            y.text = str(v.co[1]*scale)
            z.text = str(v.co[2]*scale)
            nx,ny,nz = makeXYZode(x_normal)
            nx.text = str(v.normal[0])
            ny.text = str(v.normal[1])
            nz.text = str(v.normal[2])

        loop_vert = {l.index: l.vertex_index for l in model.loops}
        
        last_tex = ''
        last_material = ''

        for f in model.polygons:
            face=ET.SubElement(x_faces,'face')
            
            
            uv_act = model.uv_layers.active
            uv_layer = uv_act.data if uv_act is not None else EmptyUV()

            if not skip_materials:
                try:
                    texfn = model.uv_textures.active.data[f.index].image.name
                except AttributeError:
                    texfn = None
                    
                if last_material != f.material_index:
                    material = ET.SubElement(face,'material')
                    mat = model.materials[f.material_index]
                    specular = ET.SubElement(material,'specular')
                    sr,sg,sb = makeRGBNode(specular)
                    sr.text = str(mat.specular_color.r*mat.specular_intensity)
                    sg.text = str(mat.specular_color.g*mat.specular_intensity)
                    sb.text = str(mat.specular_color.b*mat.specular_intensity)
                    diffuse = ET.SubElement(material, 'diffuse')
                    dr, dg, db = makeRGBNode(diffuse)
                    dr.text = str(mat.diffuse_color.r*mat.diffuse_intensity)
                    dg.text = str(mat.diffuse_color.g*mat.diffuse_intensity)
                    db.text = str(mat.diffuse_color.b*mat.diffuse_intensity)
                    shining = ET.SubElement(material,'shining')
                    shining.text = str(mat.specular_hardness)
                    emit = ET.SubElement(material,'emit')
                    emit.text = str(mat.emit)
                    last_material = f.material_index
            
                if last_tex != texfn or texfn == None:
                    texture = ET.SubElement(face,'texture')
                    texture.text = texfn
                    last_tex = texfn
                    
            vertices = ET.SubElement(face,'vertices')
            
            vpf = len(f.loop_indices)

            uvlist = []
            for li in f.loop_indices:
                uvlist.append(uv_layer[li].uv)
            uvlist.reverse()
            un = 0
            
            for li in f.loop_indices:
               coords = verts[loop_vert[li]].co 
               normal = verts[loop_vert[li]].normal
               uv = uv_layer[li].uv
               vertex = ET.SubElement(vertices, 'vertex')
               index = ET.SubElement(vertex, 'i')
               index.text = str(loop_vert[li])
               x_uvi = ET.SubElement(vertex, 'uv_i')
               x_uvi.text = str(uv_index)
               uv_index += 1
               
        return shape

    
def triangulate(model):
    print("Triangulating model")
    bm = bmesh.new()
    bm.from_mesh(model.data)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.to_mesh(model.data)
    return model