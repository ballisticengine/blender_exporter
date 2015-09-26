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

def shapeExport(model,scale=1,omit_material=False,triangulate=False,swap_xy=False):
        #print ("SE")
        loc=model.location.copy()
        shape=ET.Element('shape')
        name=ET.SubElement(shape,'name')
        loce=ET.SubElement(shape,"loc")
        lx,ly,lz=makeXYZode(loce)
        lx.text=str(loc.x)
        ly.text=str(loc.y)
        lz.text=str(loc.z)
        geom=ET.SubElement(shape,'geom')
        x_counts=ET.SubElement(geom,'counts')
        x_vcount=ET.SubElement(x_counts,'vertices')
        x_fcount=ET.SubElement(x_counts,"faces")
        x_vpf=ET.SubElement(x_counts,"v_p_f")
        x_uvcount=ET.SubElement(x_counts,'uvs')

        x_faces=ET.SubElement(geom,'faces')
        x_verts=ET.SubElement(geom,'vertices')
        x_uvs=ET.SubElement(geom,'uvs')
        uv_index=0
        name.text=model.data.name
        scene = bpy.context.scene
        oldmodel=None
        if False:#triangulate
            bpy.ops.object.mode_set(mode='OBJECT')
            model.select = True
            oldmodel=bpy.ops.object.duplicate()
            bpy.ops.object.mode_set(mode='EDIT')

            #bpy.context.scene.objects.active = model

            #bm = bmesh.new()
            #bm.from_mesh(model.data)
            bpy.ops.mesh.quads_convert_to_tris(use_beauty=False)
            bpy.ops.object.mode_set(mode='OBJECT')
            #bm.modifiers["Triangulate"].use_beauty = False
            #bpy.ops.object.modifier_apply(apply_as="DATA", modifier="Triangulate")
            #bm.to_mesh(model.data)

            model=model.data
            print ("Triangulated")

        else:
            model=model.to_mesh(scene, True, 'PREVIEW')

        """if swap_xy:
            bpy.ops.transform.rotate(value=1.57,axis=(1,0,0))
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        """
        verts = model.vertices


        x_vcount.text=str(len(verts))

        for v in verts:
            x_vertex=ET.SubElement(x_verts,'vertex')
            x_co=ET.SubElement(x_vertex,"coords")
            x_normal=ET.SubElement(x_vertex,'normal')
            x,y,z=makeXYZode(x_co)
            x.text=str(v.co[0]*scale)
            y.text=str(v.co[1]*scale)
            z.text=str(v.co[2]*scale)
            nx,ny,nz=makeXYZode(x_normal)
            nx.text=str(v.normal[0])
            ny.text=str(v.normal[1])
            nz.text=str(v.normal[2])

        loop_vert = {l.index: l.vertex_index for l in model.loops}


        last_tex=''
        last_material=''
        x_fcount.text=str(len(model.polygons))

        for f in model.polygons:
            #print (f.material_index)
            texfn=model.uv_textures.active.data[f.index].image.name
            uv_act = model.uv_layers.active
            uv_layer = uv_act.data if uv_act is not None else EmptyUV()

            face=ET.SubElement(x_faces,'face')
            if not omit_material:
                if last_material!=f.material_index:
                    material=ET.SubElement(face,'material')
                    mat=model.materials[f.material_index]
                    specular=ET.SubElement(material,'specular')
                    sr,sg,sb=makeRGBNode(specular)
                    sr.text=str(mat.specular_color.r*mat.specular_intensity)
                    sg.text=str(mat.specular_color.g*mat.specular_intensity)
                    sb.text=str(mat.specular_color.b*mat.specular_intensity)
                    diffuse=ET.SubElement(material,'diffuse')
                    dr,dg,db=makeRGBNode(diffuse)
                    dr.text=str(mat.diffuse_color.r*mat.diffuse_intensity)
                    dg.text=str(mat.diffuse_color.g*mat.diffuse_intensity)
                    db.text=str(mat.diffuse_color.b*mat.diffuse_intensity)
                    shining=ET.SubElement(material,'shining')
                    shining.text=str(mat.specular_hardness)
                    emit=ET.SubElement(material,'emit')
                    emit.text=str(mat.emit)
                    last_material=f.material_index

                vertices=ET.SubElement(face,'vertices')
                if last_tex!=texfn:
                    texture=ET.SubElement(face,'texture')
                    texture.text=texfn
                    last_tex=texfn
                else:
                    #print ("Skipping "+texfn)
                    pass
            vpf=len(f.loop_indices)

            uvlist=[]
            for li in f.loop_indices:
                uvlist.append(uv_layer[li].uv)
            uvlist.reverse()
            un=0
            for li in f.loop_indices:
               coords=verts[loop_vert[li]].co #*bpy.context.matrix_world
               normal=verts[loop_vert[li]].normal
               #print(normal)
               uv=uv_layer[li].uv
               vertex=ET.SubElement(vertices,'vertex')
               index=ET.SubElement(vertex,'i')
               index.text=str(loop_vert[li])
               x_uvi=ET.SubElement(vertex,'uv_i')
               x_uvi.text=str(uv_index)
               uv_index+=1
               x_uv=ET.SubElement(vertex,'uv')
               x_u=ET.SubElement(x_uv,'u')
               x_v=ET.SubElement(x_uv,'v')
               x_u.text=str(uv[0])
               x_v.text=str(uv[1])

        x_vpf.text=str(vpf)
        x_uvcount.text=str(uv_index)

        if oldmodel:
            print ("DEL")
            bpy.ops.object.delete()

        return shape