
from mpl_toolkits.basemap import Basemap

def readshape(filename,info="info"):

    m = Basemap(projection='merc',llcrnrlat=-80,urcrnrlat=80,\
            llcrnrlon=-180,urcrnrlon=180,lat_ts=20,resolution='c')
    shp=Basemap.readshapefile(m,filename,name=info,drawbounds=False)
    verts=m.info

    attributes=m.info_info
    return attributes,verts,shp


if __name__ == '__main__':
    a,v,shp=readshape("us48")

    poly2shape={}
    shape2poly={}
    pid=0
    maxx=maxy=-999999999
    minx=miny=10**10
    for poly in a:
        shapenum=poly['SHAPENUM']
        if shapenum in shape2poly:
            shape2poly[shapenum].append(pid)
        else:
            shape2poly[shapenum]=[pid]
        if pid in poly2shape:
            poly2shape[pid].append(shapenum)
        else:
            poly2shape[pid]=[shapenum]
        xs=[vert[0] for vert in v[pid]]
        ys=[vert[1] for vert in v[pid]]
        bx=max(xs)
        sx=min(xs)
        by=max(ys)
        sy=min(ys)
        maxx=max((maxx,bx))
        minx=min((minx,sx))
        maxy=max((maxy,by))
        miny=min((miny,sy))
        pid+=1

    import Tkinter as tk

    w=h=500
    sx=(w*1.)/(maxx-minx)
    sy=(h*1.)/(maxy-miny)
    top=tk.Tk()
    can=tk.Canvas(top, width=w,height=h, background='white')
    can.grid()
    for poly in v:
        xs=[ (p[0]-minx)*sx for p in poly]
        ys=[ h-(p[1]-miny)*sy for p in poly]
        coords=zip(xs,ys)
        can.create_polygon(coords,fill='white',outline='black')





