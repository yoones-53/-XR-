import bpy,math,pathlib
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
OUT=pathlib.Path(__file__).parent
bpy.ops.wm.open_mainfile(filepath=str(OUT/'18Building_Concept.blend'))
s=bpy.context.scene;cam=s.camera
col=bpy.data.collections.new('06_Gameplay_Workflow');s.collection.children.link(col)
def move(o):
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o)
def emit(name,c,strength=1):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;n=m.node_tree.nodes;n.clear();a=n.new('ShaderNodeEmission');a.inputs[0].default_value=(*c,1);a.inputs[1].default_value=strength;o=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(a.outputs[0],o.inputs[0]);return m
ink=emit('WF Ink',(.015,.025,.045));muted=emit('WF Muted',(.14,.19,.24));white=emit('WF White',(1,1,1),3);blue=emit('WF No anomaly',(.02,.29,.58));orange=emit('WF Anomaly',(.85,.22,.035));green=emit('WF Correct',(.035,.37,.20));red=emit('WF Reset',(.65,.035,.055));pale=emit('WF Panel',(.80,.85,.90),1.5);bluebg=emit('WF Blue tint',(.69,.81,.94),1.8);orangebg=emit('WF Orange tint',(.98,.79,.62),1.8);greenbg=emit('WF Green tint',(.71,.88,.77),1.8)
for o in bpy.data.objects:
 if o.name.startswith('Page ') or o.name=='Circulation guide' or any(o.name.startswith(x) for x in ['01 stairs','02 corridor','03 branch','04 elevator']):o.hide_render=True;o.hide_viewport=True
 if o.name=='Backdrop':o.data.materials.clear();o.data.materials.append(white)
 if o.name=='Elevator floor':o.data.materials.clear();o.data.materials.append(blue)
font=bpy.data.fonts.load(r'C:\Windows\Fonts\malgun.ttf')
s.render.resolution_x=3300;s.render.resolution_y=1980;s.render.resolution_percentage=100
cam.location=(73,-72,100);cam.rotation_euler=(Vector((9,7,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=110;cam.data.shift_x=.19
bpy.context.view_layer.update()
def plane(name,x,y,w,h,mat,z=-59):
 bpy.ops.mesh.primitive_plane_add(size=1);o=bpy.context.object;o.name=name;move(o);o.parent=cam;o.location=(x,y,z);o.rotation_euler=(0,0,0);o.scale=(w,h,1);o.data.materials.append(mat);return o
def text(body,x,y,size=1,mat=ink):
 d=bpy.data.curves.new(body,'FONT');d.body=body;d.font=font;d.size=size;d.align_x='CENTER';d.align_y='CENTER';o=bpy.data.objects.new(body,d);col.objects.link(o);o.parent=cam;o.location=(x,y,-58.5);o.data.materials.append(mat);return o
# Camera shift affects both model projection and camera-local overlay positions.
OFFSET=cam.data.shift_x*cam.data.ortho_scale
def rect(name,x,y,w,h,mat,z=-59):return plane(name,x+OFFSET,y,w,h,mat,z)
def txt(body,x,y,size=1,mat=ink):return text(body,x+OFFSET,y,size,mat)
def path(name,pts,mat=ink,width=.055,overlay=True):
 d=bpy.data.curves.new(name,'CURVE');d.dimensions='3D';d.bevel_depth=width;d.bevel_resolution=2;p=d.splines.new('POLY');p.points.add(len(pts)-1)
 for point,co in zip(p.points,pts):point.co=(*( (co[0]+OFFSET,co[1],-58.7) if overlay else co),1)
 o=bpy.data.objects.new(name,d);col.objects.link(o);o.data.materials.append(mat)
 if overlay:o.parent=cam
 return o
def arrow(name,pts,mat=ink,width=.055):
 path(name,pts,mat,width);end=Vector(pts[-1]);d=end-Vector(pts[-2]);d.normalize();n=Vector((-d.y,d.x));a=end-d*.55+n*.23;b=end-d*.55-n*.23;path(name+' tip',[tuple(a),tuple(end),tuple(b)],mat,width)
def project(p):
 v=world_to_camera_view(s,cam,Vector(p));return ((v.x-.5)*110,(v.y-.5)*66)
def box(title,x,y,w=29,h=3.4,bg=white,border=ink,sub=None):
 rect(title+' outline',x,y,w,h,border);rect(title+' fill',x,y,w-.12,h-.12,bg,-58.95)
 txt(title,x,y+(.50 if sub else 0),1.03)
 if sub:txt(sub,x,y-.74,.69,muted)
def diamond(title,x,y,w=25,h=5):
 # Two concentric diamonds form an editable decision node.
 for inset,mat,z in [(0,ink,-59),(.14,pale,-58.95)]:
  verts=[(x+OFFSET,y+h/2-inset,z),(x+OFFSET+w/2-inset,y,z),(x+OFFSET,y-h/2+inset,z),(x+OFFSET-w/2+inset,y,z)]
  mesh=bpy.data.meshes.new(title);mesh.from_pydata(verts,[],[(0,1,2,3)]);o=bpy.data.objects.new(title,mesh);col.objects.link(o);o.parent=cam;o.data.materials.append(mat)
 txt(title,x,y,1)
def callout(title,sub,x,y,target,w=17,mat=ink):
 box(title,x,y,w,3.5,white,mat,sub)
 tx,ty=project(target);dx,dy=tx-x,ty-y
 if abs(dx)>abs(dy):start=(x+(w/2+.15)*(1 if dx>0 else -1),y);elbow=((start[0]+tx)/2,y)
 else:start=(x,y+1.9*(1 if dy>0 else -1));elbow=(x,(start[1]+ty)/2)
 arrow(title+' leader',[start,elbow,(tx,ty)],mat,.05)
def route(name,points,mat):
 path(name,points,mat,.105,False)
 a=Vector(points[-2]);b=Vector(points[-1]);d=b-a;d.z=0;d.normalize();n=Vector((-d.y,d.x,0));path(name+' arrow',[tuple(b-d*.8+n*.34),tuple(b),tuple(b-d*.8-n*.34)],mat,.11,False)
# Two different decisions share the same exploratory corridor, not separate maps.
route('No anomaly route',[(.7,1,.13),(.7,25,.13),(25,25,.13),(25,20,.13)],blue)
route('Anomaly return route',[(-.7,1,.15),(-.7,-15,.15),(-.7,-19,1.05)],orange)
def sphere(name,p,scale):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=1,location=p);o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(ink);move(o)
def bone(name,a,b,r):
 d=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2);o=bpy.context.object;o.name=name;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(ink);move(o)
for x in [-.23,.23]:bone('Player leg',(x,0,.12),(x,0,1),.13)
sphere('Player body',(0,0,1.4),(.41,.25,.60));sphere('Player head',(0,0,2.2),(.29,.29,.32))
for a in [-1,1]:bone('Player arm',(a*.36,0,1.7),(a*.62,.05,1.1),.12)
# Main page and spatial callouts.
txt('18 BUILDING  |  이상현상 판단과 이동 선택',-20,29.5,1.85)
txt('같은 복도를 탐색하고, 발견한 이상현상에 따라 출구를 선택한다',-20,26.9,.83,muted)
path('Panel divider',[(13.2,-27),(13.2,26)],pale,.035)
callout('게임 시작 · 5층 진입','캐릭터 시작 위치',-43,-2,(0,0,1.6),19)
callout('이상현상 있음 → 뒤 계단','뒤로 돌아가 계단을 선택',-40,-23,(0,-20.5,2),24,orange)
callout('이상현상 없음 → 엘리베이터','복도 끝 엘리베이터를 선택',-1,-16,(25,20,.3),24,blue)
txt('공간 탐색',-20,3,1.18,ink)
txt('주변을 살펴 정상 상태와 비교',-20,1.1,.72,muted)
# Right panel: complete gameplay flow with reset and successful loop.
X=33
txt('층 진행 워크플로우',X,28.9,1.35)
box('게임 시작 · 5층 진입',X,23,28,3.5,pale)
box('층별 이상현상 결정',X,17,28,3.8,white,ink,'최초 5층 정상 튜토리얼 · 이후 무작위')
box('공간 탐색 · 이상현상 판단',X,11,28,3.5,white)
arrow('Start to generate',[(X,21.2),(X,19.1)])
arrow('Generate to explore',[(X,15),(X,12.9)])
box('있음 → 뒤 계단',25.3,4.7,14.2,3.6,orangebg,orange,'이상현상이 있다고 판단')
box('없음 → 엘리베이터',41,4.7,15.4,3.6,bluebg,blue,'이상현상이 없다고 판단')
arrow('Choose stairs',[(X,9.1),(X,8),(25.3,8),(25.3,6.65)],orange)
arrow('Choose elevator',[(X,9.1),(X,8),(41,8),(41,6.65)],blue)
diamond('선택이 올바른가?',X,-2.2,27,5.3)
arrow('Stairs to check',[(25.3,2.7),(25.3,1.5),(X,1.5),(X,.65)],orange)
arrow('Elevator to check',[(41,2.7),(41,1.5),(X,1.5)],blue)
# Incorrect selection returns to 5F, then goes through generation again.
arrow('Wrong reset',[(46.7,-2.2),(52,-2.2),(52,23),(47.2,23)],red,.075)
txt('오답',49.7,-.7,.81,red);txt('5층으로',50,20,.73,red);txt('복귀',50,18.6,.73,red)
diamond('현재 층이 1층인가?',X,-10,27,5.3)
arrow('Correct',[(X,-5),(X,-7.1)],green,.07);txt('정답',36,-6,.8,green)
box('다음 층 이동 (n-1층)',25,-19,16.8,4,greenbg,green,'이상현상을 새로 결정')
box('게임 엔딩 프로세스',43,-19,16.8,4,greenbg,green,'1층에서 정답 선택 시')
arrow('No next floor',[(25,-11.6),(25,-16.8)],green);txt('아니오',21.6,-14.7,.73,green)
arrow('Yes ending',[(41,-11.6),(43,-13.2),(43,-16.8)],green);txt('예',45.1,-14.8,.78,green)
# Return loop from next floor to new anomaly roll, along the left edge of the flow panel.
arrow('New floor loop',[(25,-21.2),(25,-24),(16.1,-24),(16.1,17),(18.8,17)],green,.06)
txt('층을 내려가며 반복',X,-26,.82,muted)
txt('정답 기준: 이상현상 있음 + 계단   /   이상현상 없음 + 엘리베이터',-20,-28,.87)
txt('공간 배치: 18Building 씬 기반   ·   계단 단순화   ·   화살표는 판단에 따른 선택 경로',-20,-30,.65,muted)
s.cycles.samples=32
s.view_settings.view_transform='Standard'
for m in [white,pale,bluebg,orangebg,greenbg]:
 next(n for n in m.node_tree.nodes if n.type=='EMISSION').inputs[1].default_value=1
s.render.filepath=str(OUT/'18Building_Gameplay_Workflow.png')
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'18Building_Gameplay_Workflow.blend'))
bpy.ops.render.render(write_still=True)
print('WORKFLOW DONE')
