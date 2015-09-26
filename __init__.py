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





class ExportXML(bpy.types.Operator,ExportHelper):
    bl_idname = "export_scene.xml_geom"
    bl_label = 'Export to XML Level Geometry'
    filename_ext = ".xml"
    scale = FloatProperty(
            name="Scale",
            description="",
            min=0.0, max=1000.0,
            default=10.0,
            )

    def execute(self, context):
        scale=self.scale
        level=ET.Element('level')
        portals=ET.SubElement(level,"portals")
        rooms=ET.SubElement(level,"rooms")
        room_dict=dict()
        loc_dict=dict()
        for object in context.selectable_objects:
            #print(object.type)
            if object is None or object.type!='MESH' or object.name.find('[OBJECT]')!=-1:
                continue
            #print (object.type)
            #print(object.name)
            #model=object.to_bmesh( bpy.context.scene, True, 'PREVIEW')
            #bpy.ops.triangulate(model, model.data.faces)

            shape=shapeExport(object,self.scale,False,True,True)
            type=ET.SubElement(shape,"type")
            type.text="level"
            room=ET.Element('room')

            loc=object.location
            location_xml=ET.SubElement(room,"location")
            x,y,z=makeXYZode(location_xml)
            x.text=str(loc.x*self.scale)
            y.text=str(loc.y*self.scale)
            z.text=str(loc.z*self.scale)
            room_dict[object.name]=room
            loc_dict[object.name]=loc
            ambient_light=ET.Element('ambient_light')
            r,g,b=makeRGBNode(ambient_light)
            try:
                r.text=str(object['ambient_r'])
                g.text=str(object['ambient_g'])
                b.text=str(object['ambient_b'])
            except KeyError:
                r.text="1.0"
                g.text="1.0"
                b.text="1.0"
            room.append(ambient_light)
            room.append(shape)
            room.append(ET.Element('entities'))
            rooms.append(room)


        for object in context.selectable_objects:
            if object is None or (object.type=='MESH' and object.name.find('[OBJECT]')==-1):
                continue

            try:
                if object['entityType']=="portal":
                    portal_x=ET.SubElement(portals,"portal")
                    loc=object.location.copy()
                    loc_x=ET.SubElement(portal_x,"location")
                    x,y,z=makeXYZode(loc_x)
                    x.text=str(loc.x*self.scale)
                    y.text=str(loc.y*self.scale)
                    z.text=str(loc.z*self.scale)
                    a_x=ET.SubElement(portal_x,"A")
                    b_x=ET.SubElement(portal_x,"B")
                    a_x.text=object["A"]
                    b_x.text=object["B"]
            except KeyError:
                pass

        for object in context.selectable_objects:
            if object is None or (object.type=='MESH' and object.name.find('[OBJECT]')==-1):
                continue
            #print(object.constraints)


            for c in object.constraints:
                if c.type=='CHILD_OF':
                    entites=room_dict[c.target.name].find('entities')
                    entity=ET.Element('entity')
                    name=ET.Element('name')
                    name.text=object.name
                    etype=ET.Element('type')
                    loc=object.location.copy()
                    rloc=loc_dict[c.target.name]
                    loc.x=loc.x+rloc.x
                    loc.y=loc.y+rloc.y
                    loc.z=loc.z+rloc.z
                    #if object.type=="EMPTY":
                    if object.name.find('[OBJECT]')!=-1:
                        etype.text=object['entityType']
                        if object['entityType']=='object' or object['entityType']=='Object':
                            ephysics=ET.Element("physics")
                            if "noPhysics" in object:
                                ephysics.text="0"
                            else:
                                ephysics.text="1"
                            emodel=ET.Element('model')
                            etex=ET.Element('texture')
                            emodel.text=object['model']
                            #etex.text=object['texture']
                            escale=ET.Element('scale')
                            escale.text=str(object['scale'])
                            entity.append(ephysics)
                            entity.append(escale)
                            entity.append(emodel)
                            entity.append(etex)
                        if object['entityType']=='bounding':
                            verts=object.data.vertices
                            #print (verts)
                            xx=-(verts[0].co[0]+loc.x)*self.scale
                            yy=-(verts[0].co[1]+loc.y)*self.scale
                            zz=-(verts[0].co[2]+loc.z)*self.scale
                            minx=maxx=xx
                            maxy=miny=yy
                            minz=maxz=zz
                            #print ("Minx",minx)
                            for v in verts:
                                xx=-(v.co[0]+loc.x)*self.scale
                                yy=-(v.co[1]+loc.y)*self.scale
                                zz=-(v.co[2]+loc.z)*self.scale
                                if xx>maxx:
                                    maxx=xx
                                if xx<minx:
                                    minx=xx

                                if yy>maxy:
                                    maxy=yy
                                if yy<miny:
                                    miny=yy

                                if zz>maxz:
                                    maxz=zz
                                if zz<minz:
                                    minz=zz
                            emin=ET.Element('min')
                            emax=ET.Element('max')
                            mx,my,mz=makeXYZode(emin)
                            ax,ay,az=makeXYZode(emax)
                            mx.text=str(minx)
                            my.text=str(miny)
                            mz.text=str(minz)
                            ax.text=str(maxx)
                            ay.text=str(maxy)
                            az.text=str(maxz)
                            entity.append(emin)
                            entity.append(emax)
                            #entites.append(entity)
                            #continue
                            print (minx,miny,minz,maxx,maxy,maxz)

                    elif object.type=="LAMP":
                        etype.text='light'
                        lamp=bpy.data.lamps[object.name]
                        energy=ET.SubElement(entity,'energy')
                        energy.text=str(lamp.energy)
                        r,g,b=makeRGBNode(entity)
                        r.text=str(lamp.color.r*lamp.energy)
                        g.text=str(lamp.color.g*lamp.energy)
                        b.text=str(lamp.color.b*lamp.energy)



                    elif object['entityType']=="JumpPoint":
                        etype.text='jumppoint'
                        loc=object.location.copy()




                    xx=loc.x*self.scale
                    yy=loc.y*self.scale
                    zz=loc.z*self.scale

                    eloc=ET.Element('location')
                    ex=ET.Element('x')
                    ey=ET.Element('y')
                    ez=ET.Element('z')
                    ex.text=str(xx)
                    ey.text=str(yy)
                    ez.text=str(zz)
                    erot=ET.Element('facing')
                    erx=ET.Element('x')
                    ery=ET.Element('y')
                    erz=ET.Element('z')

                    position, quaternion, scale = object.matrix_world.decompose()
                    rot = object.rotation_euler
                    erx.text=str(rot.x)
                    ery.text=str(rot.y)
                    erz.text=str(rot.z)
                    eloc.append(ex)
                    eloc.append(ey)
                    eloc.append(ez)

                    erot.append(erx)
                    erot.append(ery)
                    erot.append(erz)

                    entity.append(name)
                    entity.append(etype)
                    entity.append(eloc)
                    entity.append(erot)
                    entites.append(entity)



            #print (object.type)
        tree = ET.ElementTree(level)
        keywords = self.as_keywords()
        f=open(self.filepath,"wb")
        print (self.filepath)
        tree.write(f)
        #tree.close()
        f.close()
        return {'FINISHED'}

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
    animation = BoolProperty(name="Animated",description="",default=False)

    def exportBounds(self):
        bounds=ET.Element('bounds')
        for object in self.context.selectable_objects:
            if object is not None and object.type=='MESH' and object.name.find('[BOUNDING]')!=-1:
                bound=ET.SubElement(bounds,"bound")
                verts=object.data.vertices
                loc=object.location.copy()
                xx=(verts[0].co[0])
                yy=(verts[0].co[1])
                zz=(verts[0].co[2])
                minx=maxx=xx
                maxy=miny=yy
                minz=maxz=zz
                for v in verts:
                    xx=(v.co[0])
                    yy=(v.co[1])
                    zz=(v.co[2])
                    if xx>maxx:
                        maxx=xx
                    if xx<minx:
                        minx=xx

                    if yy>maxy:
                        maxy=yy
                    if yy<miny:
                        miny=yy

                    if zz>maxz:
                        maxz=zz
                    if zz<minz:
                        minz=zz
                emin=ET.Element('min')
                emax=ET.Element('max')
                eloc=ET.Element('loc')
                ex,ey,ez=makeXYZode(eloc)
                ex.text=str(loc.x)
                ey.text=str(loc.y)
                ez.text=str(loc.z)
                mx,my,mz=makeXYZode(emin)
                ax,ay,az=makeXYZode(emax)
                mx.text=str(minx)
                my.text=str(miny)
                mz.text=str(minz)
                ax.text=str(maxx)
                ay.text=str(maxy)
                az.text=str(maxz)
                bound.append(emin)
                bound.append(emax)
                bound.append(eloc)
                name=ET.SubElement(bound,"name")
                name.text=object.name


        return bounds



    def execute(self, context):
        self.context=context
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        shape=shapeExport(context.active_object,self.scale,False,True)

        bounds=self.exportBounds()
        shape.append(bounds)
        type=ET.SubElement(shape,"type")
        frame_times=list()
        frame_times.append(0)
        if self.animation:
            """for key in bpy.data.actions[0].fcurves:
                for marker in key.keyframe_points:
                    frame = marker.co.x
                    print ("Frame",frame)
                    frame_time = frame_to_time(frame)
                    frame_times.append(frame_time)
                    print(frame, frame_time)
                break
            """
            frame_i=0
            for k, v in bpy.context.scene.timeline_markers.items():
                frame = v.frame
                frame_time = frame_to_time(frame)
                frame_times.append(frame_time)
                if(frame_i>0):
                    frame_times[frame_i]-=frame_times[frame_i-1]
                frame_i+=1
            #print(dir(action))
            print(frame_times)
            type.text="animation"
            root=ET.Element("animation")
            import bmesh
            bm = bmesh.new()

            bm.from_mesh(context.active_object.data)
            print ("Animation")
            #(start_frame, end_frame) = context.active_object.animation_data.action.frame_range
            #print (dir(context.active_object.animation_data.action.frame_range))
            frames=ET.SubElement(shape,"frames")
            fcount=ET.SubElement(shape,"frame_count")
            frame_i=0;
            fcount.text=str(len(bm.verts.layers.shape.keys()))
            for key in bm.verts.layers.shape.keys():
                val = bm.verts.layers.shape.get(key)
                sk=context.active_object.data.shape_keys.key_blocks[key]
                #print(dir(sk.bl_rna))
                print("v=%f, f=%f, sm=%f,smax=%f" % ( sk.value, sk.frame,sk.slider_min,sk.slider_max))
                #print(dir(sk))
                frame=ET.Element("frame")
                fnum=ET.SubElement(frame,"fnum")
                fval=ET.SubElement(frame,"fval")
                ftime=ET.SubElement(frame,"ftime")
                fnum.text=str(sk.frame)
                fval.text=str(sk.value)
                ftime.text=str(frame_times[frame_i]) #str(frame_times[frame_i])
                frame_verts=ET.SubElement(frame,"vertices")
                for i in range(len(bm.verts)):
                    vertex=ET.Element("vertex")
                    x,y,z=makeXYZode(vertex)
                    v = bm.verts[i]
                    x.text=str(v[val][0])
                    y.text=str(v[val][1])
                    z.text=str(v[val][2])
                    #delta = v[val] - v.co
                    delta = v[val] - v.co
                    if (delta.length > 0):
                        print ( "v[%d]+%s" % ( i,delta) )

                    frame_verts.append(vertex)
                frame_i+=1
                frames.append(frame)
        else:
            type.text="static"
        tree = ET.ElementTree(shape)
        f=open(self.filepath,"wb")
        print (self.filepath)
        tree.write(f)
        f.close()
        #room_dict[object.name]=room
        #room.append(shape)
        #room.append(ET.Element('entities'))
        #level.append(room)
        return {'FINISHED'}



def menu_func_export(self, context):
    self.layout.operator(ExportXML.bl_idname, text="XML Geomerty (.xml)")
    self.layout.operator(ExportXMLModel.bl_idname, text="XML Model (.xml)")



def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()