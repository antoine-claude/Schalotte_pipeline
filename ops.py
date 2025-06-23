import bpy
import importlib
from . import utils
importlib.reload(utils) 

#New properties to store data about manifold
class CheckItem(bpy.types.PropertyGroup):
    object_name: bpy.props.StringProperty()
    vert_mani: bpy.props.IntProperty()
    vert_count: bpy.props.IntProperty()
    is_origin: bpy.props.BoolProperty()
    is_rot: bpy.props.BoolProperty()
    is_scale: bpy.props.BoolProperty()
#    is_valid: bpy.props.BoolProperty()

#Class check all object if they are non manifold
class OBJECT_OT_run_check(bpy.types.Operator):
    bl_idname = "object.run_check"
    bl_label = "Run Manifold Check"

    def execute(self, context):
        scene = context.scene
        scene.check_items.clear()
        for obj in scene.objects:
            if obj.type != 'MESH':continue
        
            item = scene.check_items.add()
            item.object_name = obj.name
            item.is_origin = utils.IsOnWorldOrigin(obj)
            item.is_rot = utils.IsRotationApplied(obj)
            item.is_scale = utils.IsScaleApplied(obj)

            result = utils.is_vertex_manifold(obj, False)
            if result:
                item.vert_mani = len(result)
                item.vert_count = len(obj.data.vertices)
#                item.is_valid = True
        return {'FINISHED'}

#Class for Select button on non manifold object
class OBJECT_OT_check_manifold(bpy.types.Operator):
    bl_idname = "object.check_manifold"
    bl_label = ""

    select_mode: bpy.props.BoolProperty(default=False)
    target_name: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.target_name)
        if not obj:
            self.report({'ERROR'}, f"Objet introuvable : {self.target_name}")
            return {'CANCELLED'}

        verts = utils.is_vertex_manifold(obj, self.select_mode)

        if not verts:
            self.report({'INFO'}, "Tous les sommets sont manifold")
        else:
            self.report({'INFO'}, f"{len(verts)} sommets non-manifold dans {obj.name}")

        return {'FINISHED'}
