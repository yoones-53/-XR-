import bpy,pathlib
from mathutils import Vector
out=pathlib.Path(__file__).parent
bpy.ops.wm.open_mainfile(filepath=str(out/'18Building_Concept.blend'))
s=bpy.context.scene;c=s.camera
title=bpy.data.objects['Page 18 BUILDING'];sub=bpy.data.objects['Page 공간 구성 · 기획용 블록아웃']
orig=[(o,o.location.copy(),o.data.size) for o in [title,sub]]
title.location.x=-27;title.data.size=2.0;sub.location.x=-27;sub.data.size=.70
c.location=(13,7,110);c.rotation_euler=(Vector((13,7,0))-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=94
for o in bpy.data.objects:
 if o.name.startswith('Page 01 '):o.location.y=-33
 if o.name.startswith('Page 18Building.unity'):o.location.y=-35.1
s.render.filepath=str(out/'18Building_TopView.png');bpy.ops.render.render(write_still=True)
# Keep a second camera with the verified plan composition.
plan=c.copy();plan.data=c.data.copy();plan.name='Top View Camera';s.collection.objects.link(plan)
for o,loc,size in orig:o.location=loc;o.data.size=size
for o in bpy.data.objects:
 if o.name.startswith('Page 01 '):o.location.y=-25
 if o.name.startswith('Page 18Building.unity'):o.location.y=-27.1
c.location=(73,-72,100);c.rotation_euler=(Vector((9,7,0))-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=79;s.render.filepath=str(out/'18Building_Overview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'18Building_Concept.blend'))
