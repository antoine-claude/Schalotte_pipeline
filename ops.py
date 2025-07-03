import bpy
import importlib
from . import utils
importlib.reload(utils) 

#New properties to store data about manifold
class CheckItem(bpy.types.PropertyGroup):
    object_name: bpy.props.StringProperty()
    is_origin: bpy.props.BoolProperty()
    is_rot: bpy.props.BoolProperty()
    is_scale: bpy.props.BoolProperty()
    is_collection: bpy.props.BoolProperty()
    vert_overlap: bpy.props.IntProperty()
    vert_count: bpy.props.IntProperty()
    vert_mani: bpy.props.IntProperty()
    uv_overlap: bpy.props.BoolProperty()
    is_hide: bpy.props.BoolProperty()
    clean_normal: bpy.props.IntProperty()
    is_ngone: bpy.props.IntProperty() 
    is_tri: bpy.props.IntProperty()
    is_anim: bpy.props.BoolProperty()
#    is_valid: bpy.props.BoolProperty()

#Class check all object if they are non manifold
class OBJECT_OT_run_check(bpy.types.Operator):
    bl_idname = "object.run_check"
    bl_label = "Run Manifold Check"
    bl_context = "object"
    def execute(self, context):
        scene = context.scene
        scene.check_items.clear()
        for obj in scene.objects:
            if obj.type != 'MESH' or obj.name.startswith('WGT') :continue
            # if not utils.is_object_in_collection_and_subcollections(obj,bpy.data.collections['MESH']):continue
            print('nouvelle boucle')
            print(obj.name)
            item = scene.check_items.add()
            item.object_name = obj.name
            # item.is_collection = utils.IsInCollection(obj)
            item.is_origin = not utils.IsOnWorldOrigin(obj)
            item.is_rot = not utils.IsRotationApplied(obj)
            item.is_scale = not utils.IsScaleApplied(obj)
            item.uv_overlap = utils.has_uv_overlap(obj)
            item.vert_overlap = len(utils.is_vertex_overlap(obj))
            item.clean_normal = utils.flip_face_if_not_contiguous(obj)
            item.is_ngone = utils.is_polygon_valid(obj, type='ngone')
            item.is_tri = utils.is_polygon_valid(obj, type='tri')
            item.is_hide = obj.hide_get() or obj.hide_viewport
            item.is_anim = utils.is_animated(obj)

            result = utils.is_vertex_manifold(obj, False)
            if result:
                item.vert_mani = len(result)
                item.vert_count = len(obj.data.vertices)


        utils.remove_empty_check_items(context.scene)
        return {'FINISHED'}

#Class for Select button on non manifold object
class OBJECT_OT_select_manifold(bpy.types.Operator):
    bl_idname = "object.select_manifold"
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


class OBJECT_OT_select_vert_dupli(bpy.types.Operator):
    bl_idname = "object.select_vertices_dupli"
    bl_label = ""
    
    target_name: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.target_name)
        if not obj:
            self.report({'ERROR'}, f"Objet introuvable : {self.target_name}")
            return {'CANCELLED'}
        
        utils.is_vertex_overlap(obj, select = True)

        return {'FINISHED'}


class OBJECT_OT_select_normal(bpy.types.Operator):
    bl_idname = "object.select_normal"
    bl_label = ""
    
    target_name: bpy.props.StringProperty()
    flip: bpy.props.BoolProperty(default=False)

    def execute(self, context):
        obj = bpy.data.objects.get(self.target_name)
        if not obj:
            self.report({'ERROR'}, f"Objet introuvable : {self.target_name}")
            return {'CANCELLED'}
        
        utils.flip_face_if_not_contiguous(obj, select=True, flip=self.flip)

        return {'FINISHED'}
    
class OBJECT_OT_select_invalid_poly(bpy.types.Operator):
    bl_idname = "object.select_invalid_poly"
    bl_label = ""
    
    target_name: bpy.props.StringProperty()
    shape: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.target_name)
        if not obj:
            self.report({'ERROR'}, f"Objet introuvable : {self.target_name}")
            return {'CANCELLED'}
        
        utils.is_polygon_valid(obj, select=True, type=self.shape)

        return {'FINISHED'}

class OBJECT_OT_clean_anim(bpy.types.Operator):
    bl_idname = "object.clean_anim"
    bl_label = ""
    
    target_name: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.target_name)
        if not obj:
            self.report({'ERROR'}, f"Objet introuvable : {self.target_name}")
            return {'CANCELLED'}
        
        obj.animation_data_clear()

        return {'FINISHED'}