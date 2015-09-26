def bounding(verts,loc,scale=1):
    xx=-(verts[0].co[0]+loc.x)*scale
    yy=-(verts[0].co[1]+loc.y)*scale
    zz=-(verts[0].co[2]+loc.z)*scale
    minx=maxx=xx
    maxy=miny=yy
    minz=maxz=zz
    for v in verts:
        xx=-(v.co[0]+loc.x)*scale
        yy=-(v.co[1]+loc.y)*scale
        zz=-(v.co[2]+loc.z)*scale
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
        return (maxx,minx,maxy,miny,maxz,minz)