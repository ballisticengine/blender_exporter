import bmesh

def export_animation(shape): 
    frame_times = list()
    frame_times.append(0)
    frame_i = 0
    for k, v in bpy.context.scene.timeline_markers.items():
        frame = v.frame
        frame_time = frame_to_time(frame)
        frame_times.append(frame_time)
        if(frame_i > 0):
            frame_times[frame_i] -= frame_times[frame_i-1]
        frame_i += 1
           
            
    root = ET.Element("animation")
    
    bm = bmesh.new()
    bm.from_mesh(context.active_object.data)
    frames = ET.SubElement(shape, "frames")
    fcount = ET.SubElement(shape, "frame_count")
    frame_i = 0;
    fcount.text = str(len(bm.verts.layers.shape.keys()))
    for key in bm.verts.layers.shape.keys():
        val = bm.verts.layers.shape.get(key)
        sk = context.active_object.data.shape_keys.key_blocks[key]
        #print(dir(sk.bl_rna))
        print("v=%f, f=%f, sm=%f,smax=%f" % (sk.value, sk.frame, sk.slider_min, sk.slider_max))
        #print(dir(sk))
        frame = ET.Element("frame")
        fnum = ET.SubElement(frame, "fnum")
        fval = ET.SubElement(frame, "fval")
        ftime = ET.SubElement(frame, "ftime")
        fnum.text = str(sk.frame)
        fval.text = str(sk.value)
        ftime.text = str(frame_times[frame_i]) #str(frame_times[frame_i])
        frame_verts = ET.SubElement(frame, "vertices")
        for i in range(len(bm.verts)):
            vertex = ET.Element("vertex")
            x, y, z = makeXYZode(vertex)
            v = bm.verts[i]
            x.text = str(v[val][0])
            y.text = str(v[val][1])
            z.text = str(v[val][2])
            #delta = v[val] - v.co
            delta = v[val] - v.co
            if (delta.length > 0):
                print ("v[%d]+%s" % (i, delta))

            frame_verts.append(vertex)
        frame_i += 1
                frames.append(frame)

