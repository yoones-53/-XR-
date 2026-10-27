import bpy,math,json,pathlib
from mathutils import Vector,Matrix
OUT=pathlib.Path(__file__).parent
items=json.loads((OUT/'unity_geometry.json').read_text(encoding='utf-8'))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
def collection(name):
 c=bpy.data.collections.new(name);scene.collection.children.link(c);return c
arch=collection('01_Architecture');detail=collection('02_Doors_Windows');stairs=collection('03_Stairs_Schematic');anno=collection('04_Labels');stage=collection('05_Presentation');raw=collection('90_Unity_Primitives_Reference_HIDDEN')
def mat(name,color):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.76
 return m
wall=mat('Warm ivory walls',(.72,.77,.76));floor=mat('Corridor pale ivory',(.87,.89,.85));base=mat('Plinth',(.20,.29,.34));blue=mat('Window blue',(.26,.62,.70));gold=mat('Door ochre',(.74,.42,.17));teal=mat('Elevator teal',(.06,.39,.44));stairmat=mat('Stair sandstone',(.70,.62,.47));ink=mat('Text navy',(.045,.10,.14));muted=mat('Text secondary',(.25,.36,.40));white=mat('White',(.95,.97,.95));red=mat('Poster rust',(.73,.28,.16))
def move(o,c):
 for co in list(o.users_collection):co.objects.unlink(o)
 c.objects.link(o)
def cube(name,loc,dim,material,c=arch,bevel=.035):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material);move(o,c)
 if bevel:
  mod=o.modifiers.new('Soft edges','BEVEL');mod.width=bevel;mod.segments=2;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o
font=bpy.data.fonts.load(r'C:\Windows\Fonts\malgun.ttf')
def text(name,body,loc,size=.65,material=ink,rot=None,c=anno):
 curve=bpy.data.curves.new(name,'FONT');curve.body=body;curve.font=font;curve.size=size;curve.align_x='CENTER';curve.align_y='CENTER';curve.extrude=0
 o=bpy.data.objects.new(name,curve);c.objects.link(o);o.location=loc
 if rot:o.rotation_euler=rot
 o.data.materials.append(material);return o
# Preserve native Unity primitive geometry as an optional reference collection.
C=Matrix(((1,0,0,0),(0,0,1,0),(0,1,0,0),(0,0,0,1)))
for i,item in enumerate(items):
 mid=item['mesh']
 if mid not in (10202,10209,10210):continue
 if mid==10202:bpy.ops.mesh.primitive_cube_add(size=1)
 elif mid==10209:bpy.ops.mesh.primitive_plane_add(size=10);bpy.context.object.rotation_euler=(math.pi/2,0,0);bpy.ops.object.transform_apply(location=False,rotation=True,scale=False)
 else:bpy.ops.mesh.primitive_plane_add(size=1);bpy.context.object.rotation_euler=(math.pi/2,0,0);bpy.ops.object.transform_apply(location=False,rotation=True,scale=False)
 o=bpy.context.object;o.name='REF_'+item['name'];o.matrix_world=C@Matrix(item['matrix']);move(o,raw)
raw.hide_render=True;raw.hide_viewport=True
# Floor tile footprints from the source prefab (Unity plane is 10 x 10).
tiles=[]
for it in items:
 if '/Floor/Plane' not in it['name'] or it['mesh']!=10209:continue
 m=Matrix(it['matrix']);p=m.translation;s=m.to_scale()
 if abs(p.y)>.1:continue
 x,y=round(p.x,2),round(p.z,2);w,d=round(s.x*10,2),round(s.z*10,2)
 if w<3.9 or d<4.9:continue
 if any(abs(x-a)<.1 and abs(y-b)<.1 for a,b,_,_ in tiles):continue
 tiles.append((x,y,w,d))
for x,y,w,d in tiles:
 cube('Floor source %.1f %.1f'%(x,y),(x,y,-.12),(w-.025,d-.025,.24),floor)
 cube('Floating plinth',(x,y,-.44),(w+.25,d+.25,.42),base,stage)
# Low cut walls expose the circulation. Door openings follow source positions.
doors=[]
for it in items:
 if '/Cube (2)' in it['name'] and 'Door' in it['name']:
  p=Matrix(it['matrix']).translation
  if -.5<p.y<3 and p.x>-4 and p.x<34:doors.append((p.x,p.z))
def wall_segments(axis,fixed,start,end,openings,name,height=1.15):
 intervals=sorted((max(start,v-.83),min(end,v+.83)) for v in openings if start<v<end)
 cur=start
 for a,b in intervals+[(end,end)]:
  if a>cur:
   center=(a+cur)/2;length=a-cur
   loc=(fixed,center,height/2) if axis=='y' else (center,fixed,height/2)
   dim=(.16,length,height) if axis=='y' else (length,.16,height)
   cube(name,loc,dim,wall)
  cur=max(cur,b)
wall_segments('y',-2.5,-17.5,37.5,[y for x,y in doors if x<0],'West cut wall')
wall_segments('y',2.5,-17.5,22.5,[y for x,y in doors if x>0 and x<4],'East cut wall')
wall_segments('y',2.5,27.5,37.5,[],'East north wall')
wall_segments('x',37.5,-2.5,2.5,[],'North end')
wall_segments('x',27.5,2.5,32.5,[x for x,y in doors if y>27],'Branch outer wall')
wall_segments('x',22.5,2.5,32.5,[20,25],'Branch inner wall')
wall_segments('y',32.5,22.5,27.5,[],'Branch end')
for x,y in doors:
 axis='y' if x<4 else 'x'
 cube('Door source location',(x,y,.73),(.18,1.28,1.46) if axis=='y' else (1.28,.18,1.46),gold,detail)
 cube('Door threshold',(x,y,.035),(.45,1.55,.07) if axis=='y' else (1.55,.45,.07),gold,detail)
# Window rhythm follows Ceil_Window floor modules; glass is symbolized at cut height.
for x,y,w,d in tiles:
 if x==0 and -1<y<21:
  cube('Window band',(2.5,y,.85),(.12,3.1,.66),blue,detail)
  for off in [-1.5,0,1.5]:cube('Window mullion',(2.5,y+off,.86),(.19,.07,.76),white,detail)
 elif 4<x<17 and y==25:
  cube('Window band',(x,22.5,.85),(3.1,.12,.66),blue,detail)
  for off in [-1.5,0,1.5]:cube('Window mullion',(x+off,22.5,.86),(.07,.19,.76),white,detail)
# Elevator bay is explicitly present at Unity (25, 20), with trigger at (25, 19).
cube('Elevator floor',(25,20,.015),(3.9,4.9,.10),teal)
cube('Elevator back',(25,17.5,.8),(4,.16,1.6),wall)
for x in [23,27]:cube('Elevator side',(x,20,.8),(.16,5,1.6),wall)
for x in [24.48,25.52]:cube('Elevator door',(x,22.35,.85),(.99,.14,1.7),teal,detail)
cube('Elevator center seam',(25,22.26,.85),(.035,.03,1.7),white,detail)
# Stair circulation is an explanatory blockout; source stairs span floors below and above.
cube('Stair footprint',(0,-20.5,-.13),(5,6.2,.26),stairmat,stairs)
for i in range(12):
 cube('Stair tread %02d'%i,(-1.2,-17.6-i*.3,.10+i*.15),(2.25,.30,.20),stairmat,stairs,.015)
cube('Stair landing',(0,-22.25,1.86),(4.85,2,.20),stairmat,stairs)
for i in range(11):cube('Return tread %02d'%i,(1.2,-21+i*.3,1.90+i*.15),(2.25,.30,.20),stairmat,stairs,.015)
for x in [-2.5,2.5]:cube('Stair cut side',(x,-20.5,.55),(.14,6.2,1.1),wall,stairs)
# Posters from exact source positions, with restrained accent color.
for y in [3.4,4.6,13.9,15.1]:cube('Poster marker',(-2.36,y,1.30),(.08,.75,.70),red,detail)
def line(name,points,material,width=.06):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=width;c.bevel_resolution=2;s=c.splines.new('POLY');s.points.add(len(points)-1)
 for p,co in zip(s.points,points):p.co=(*co,1)
 o=bpy.data.objects.new(name,c);anno.objects.link(o);o.data.materials.append(material);return o
line('Circulation guide',[(0,-14,.08),(0,25,.08),(30,25,.08)],teal,.055)
def disc(name,pos,num):
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.70,depth=.05,location=pos);o=bpy.context.object;o.name=name;move(o,anno);o.data.materials.append(teal)
 text(name+' number',str(num),(pos[0],pos[1],pos[2]+.033),.67,white)
disc('01 stairs',(0,-15,.10),1);disc('02 corridor',(0,9,.10),2);disc('03 branch',(12,25,.10),3);disc('04 elevator',(25,20,.10),4)
scene.world.color=(.8,.8,.8);scene.world.use_nodes=True
bg=next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.82,.87,.88,1);bg.inputs[1].default_value=.8
cube('Backdrop',(10,7,-1.15),(200,200,.25),mat('Background',(.89,.92,.92)),stage,.0)
def area(name,loc,power,size):
 data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;o=bpy.data.objects.new(name,data);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((10,7,0))-o.location).to_track_quat('-Z','Y').to_euler()
area('Large softbox',(-25,-15,65),32000,45);area('Fill',(45,40,45),18000,35)
try:scene.render.engine='CYCLES'
except:pass
scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.resolution_x=2000;scene.render.resolution_y=1600;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='AgX'
camera_data=bpy.data.cameras.new('Planning Camera');camera=bpy.data.objects.new('Planning Camera',camera_data);scene.collection.objects.link(camera);scene.camera=camera;camera_data.type='ORTHO';camera_data.ortho_scale=79
headers=[]
def camera_label(body,x,y,size,material=ink):
 o=text('Page '+body,body,(0,0,0),size,material,c=stage);o.parent=camera;o.location=(x,y,-90);o.rotation_euler=(0,0,0);headers.append(o);return o
camera_label('18 BUILDING',-21,27,2.4)
camera_label('공간 구성 · 기획용 블록아웃',-20.8,24.4,.80,muted)
camera_label('01 계단     02 주 복도     03 분기 복도     04 엘리베이터',0,-25,.86)
camera_label('18Building.unity 배치 기반  /  천장 생략 · 벽체 축소 · 계단 단순화',0,-27.1,.62,muted)
def setcam(loc,target):
 camera.location=loc;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
setcam((73,-72,100),(9,7,0))
scene.render.filepath=str(OUT/'18Building_Overview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'18Building_Concept.blend'))
bpy.ops.render.render(write_still=True)
setcam((13,7,110),(13,7,0));camera_data.ortho_scale=80
scene.render.filepath=str(OUT/'18Building_TopView.png');bpy.ops.render.render(write_still=True)
setcam((73,-72,100),(9,7,0));camera_data.ortho_scale=79;scene.render.filepath=str(OUT/'18Building_Overview.png')
for screen in bpy.data.screens:
 for a in screen.areas:
  if a.type=='VIEW_3D':
   a.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'18Building_Concept.blend'))
print('DONE',len(tiles),'floor modules',len(doors),'doors')
