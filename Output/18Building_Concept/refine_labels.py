import bpy,pathlib
from mathutils import Vector
out=pathlib.Path(__file__).parent
bpy.ops.wm.open_mainfile(filepath=str(out/'18Building_Concept.blend'))
s=bpy.context.scene
for name,color in [('Text navy',(.025,.065,.09)),('Text secondary',(.09,.16,.19))]:
 m=bpy.data.materials[name];nodes=m.node_tree.nodes;nodes.clear();e=nodes.new('ShaderNodeEmission');e.inputs[0].default_value=(*color,1);e.inputs[1].default_value=1;o=nodes.new('ShaderNodeOutputMaterial');m.node_tree.links.new(e.outputs[0],o.inputs[0])
s.cycles.samples=24
cam=s.camera
def view(loc,target,scale,path):
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;s.render.filepath=str(out/path)
view((73,-72,100),(9,7,0),79,'18Building_Overview.png');bpy.ops.render.render(write_still=True)
view((13,7,110),(13,7,0),80,'18Building_TopView.png');bpy.ops.render.render(write_still=True)
view((73,-72,100),(9,7,0),79,'18Building_Overview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'18Building_Concept.blend'))
