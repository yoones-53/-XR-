import bpy,math,pathlib
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
OUT=pathlib.Path(__file__).parent
bpy.ops.wm.open_mainfile(filepath=str(OUT/'18Building_Concept.blend'))
s=bpy.context.scene;cam=s.camera
notes=bpy.data.collections.new('06_Movement_And_Area_Labels');s.collection.children.link(notes)
def move(o):
 for c in list(o.users_collection):c.objects.unlink(o)
 notes.objects.link(o)
def emission(name,col):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True;n=m.node_tree.nodes;n.clear();a=n.new('ShaderNodeEmission');a.inputs[0].default_value=(*col,1);o=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(a.outputs[0],o.inputs[0]);return m
red=emission('Walkable area red',(.82,.025,.035));black=emission('Annotation ink',(.018,.025,.03));white=emission('Annotation white',(1,1,1));orange=emission('Annotation orange',(.95,.30,.055));navy=emission('Character navy',(.025,.065,.12));amber=emission('Stair highlight',(.95,.47,.08));cyan=emission('Elevator highlight',(.02,.45,.63))
next(n for n in white.node_tree.nodes if n.type=='EMISSION').inputs[1].default_value=2.5
amber.use_nodes=True;amber.node_tree.nodes.clear();p=amber.node_tree.nodes.new('ShaderNodeBsdfPrincipled');p.inputs['Base Color'].default_value=(.65,.31,.08,1);p.inputs['Roughness'].default_value=.8;output=amber.node_tree.nodes.new('ShaderNodeOutputMaterial');amber.node_tree.links.new(p.outputs[0],output.inputs[0])
for o in bpy.data.objects:
 if o.name.startswith('Floor source'):
  o.data.materials.clear();o.data.materials.append(red)
 if o.name.startswith('Page ') or o.name=='Circulation guide' or any(o.name.startswith(v) for v in ['01 stairs','02 corridor','03 branch','04 elevator']):
  o.hide_render=True;o.hide_viewport=True
 if o.name=='Backdrop':o.data.materials.clear();o.data.materials.append(white)
 if o.name=='Elevator floor':o.data.materials.clear();o.data.materials.append(cyan)
 if o.name.startswith(('Stair tread','Return tread','Stair landing','Stair footprint')):
  o.data.materials.clear();o.data.materials.append(amber)
# Player root is placed at Unity (0,0,0) by the scene prefab overrides.
# A simple schematic person marks the actual player start, rather than the old area number.
def sphere(name,loc,scale,material):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=1,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(material);move(o);return o
def bone(name,a,b,r,material):
 d=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2);o=bpy.context.object;o.name=name;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(material);move(o)
bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=1.25,depth=.08,location=(0,0,.065));o=bpy.context.object;o.name='START marker';o.data.materials.append(white);move(o)
for x in [-.25,.25]:
 bone('Player leg',(x,0,.15),(x,0,.94),.14,navy)
sphere('Player torso',(0,0,1.33),(.43,.25,.59),navy)
sphere('Player head',(0,0,2.13),(.30,.30,.33),navy)
bone('Player left arm',(-.38,0,1.60),(-.60,.08,1.04),.12,navy);bone('Player right arm',(.38,0,1.60),(.60,.08,1.04),.12,navy)
font=bpy.data.fonts.load(r'C:\Windows\Fonts\malgun.ttf')
def plane(name,x,y,w,h,mat,z=-59):
 bpy.ops.mesh.primitive_plane_add(size=1);o=bpy.context.object;o.name=name;move(o);o.parent=cam;o.location=(x,y,z);o.rotation_euler=(0,0,0);o.scale=(w,h,1);o.data.materials.append(mat);return o
def label(body,x,y,size=1,mat=black):
 d=bpy.data.curves.new('Label '+body,'FONT');d.body=body;d.font=font;d.align_x='CENTER';d.align_y='CENTER';d.size=size
 o=bpy.data.objects.new('Label '+body,d);notes.objects.link(o);o.parent=cam;o.location=(x,y,-58.7);o.data.materials.append(mat);return o
def line(name,pts,mat=orange,width=.055):
 d=bpy.data.curves.new(name,'CURVE');d.dimensions='3D';d.bevel_depth=width;d.bevel_resolution=1;p=d.splines.new('POLY');p.points.add(len(pts)-1)
 for v,co in zip(p.points,pts):v.co=(*co,-58.8,1)
 o=bpy.data.objects.new(name,d);notes.objects.link(o);o.parent=cam;o.data.materials.append(mat)
def screen(world):
 p=world_to_camera_view(s,cam,Vector(world));w=cam.data.ortho_scale;h=w*s.render.resolution_y/s.render.resolution_x;return ((p.x-.5)*w,(p.y-.5)*h)
def callout(body,x,y,target,w=11):
 plane('Callout border',x,y,w,3.25,orange);plane('Callout fill',x,y,w-.14,3.11,white,-58.95);label(body,x,y,1.05)
 tx,ty=screen(target)
 if abs(tx-x)>abs(ty-y):
  start=(x+(w/2+.1)*(1 if tx>x else -1),y);middle=((start[0]+tx)/2,y)
 else:
  start=(x,y+(-1.7 if ty<y else 1.7));middle=(x,(start[1]+ty)/2)
 line('Leader '+body,[start,middle,(tx,ty)])
 d=Vector((tx-middle[0],ty-middle[1]));d.normalize();n=Vector((-d.y,d.x));tip=Vector((tx,ty));a=tip-d*.65+n*.27;b=tip-d*.65-n*.27
 line('Arrow '+body,[tuple(a),tuple(tip),tuple(b)],width=.07)
def header(top=False):
 label('18 BUILDING  |  공간 구성',-29 if top else -20,27.1,1.35 if top else 1.75)
 label('캐릭터 이동 가능 영역 및 주요 지점',-29 if top else -20,24.9,.65 if top else .83)
 plane('Legend border',24,-24.8,22,4.2,black);plane('Legend background',24,-24.8,21.86,4.06,white,-58.95)
 plane('Legend red',17,-24.8,5,2,red,-58.85);label('이동 가능 영역',26.1,-24.8,1.02)
 label('빨강: 복도 이동 영역   /   주황: 계단 공간   /   파랑: 엘리베이터 공간',0,-28.6,.70)
def clear_overlay():
 for o in list(notes.objects):
  if o.parent==cam:bpy.data.objects.remove(o,do_unlink=True)
def annotate(top=False):
 header(top)
 if not top:
  callout('게임 시작지점',-27,-2,(0,0,1.4),12)
  callout('시작지점 뒤 · 계단 공간',-25,-20,(0,-20.5,2),16)
  callout('엘리베이터 공간',27,7,(25,20,.2),13)
 else:
  callout('게임 시작지점',-27,-7,(0,0,1.4),12)
  callout('시작지점 뒤 · 계단 공간',-27,-21,(0,-20.5,2),16)
  callout('엘리베이터 공간',27,6,(25,20,.2),13)
def camera(loc,target,scale):
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;bpy.context.view_layer.update()
s.cycles.samples=24;s.render.resolution_x=2200;s.render.resolution_y=1760
camera((73,-72,100),(9,7,0),79);annotate()
s.render.filepath=str(OUT/'18Building_Movement_Overview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'18Building_Movement.blend'))
bpy.ops.render.render(write_still=True)
clear_overlay();camera((13,7,110),(13,7,0),94);annotate(True)
s.render.filepath=str(OUT/'18Building_Movement_TopView.png');bpy.ops.render.render(write_still=True)
clear_overlay();camera((73,-72,100),(9,7,0),79);annotate();s.render.filepath=str(OUT/'18Building_Movement_Overview.png')
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'18Building_Movement.blend'))
print('DONE start Unity (0,0,0) / stairs (0,-20.5) / elevator (25,20)')
