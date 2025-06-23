import bpy 
import math
import bmesh
THRESHOLD = 0.001
#Utils check transform, main function
def IsOnWorldOrigin(Object: bpy.types.Object):
    return math.isclose(Object.location[0], 0, abs_tol=THRESHOLD) and \
           math.isclose(Object.location[1], 0, abs_tol=THRESHOLD) and \
           math.isclose(Object.location[2], 0, abs_tol=THRESHOLD)


def IsScaleApplied(Object: bpy.types.Object):
    return math.isclose(Object.scale[0], 1, abs_tol=THRESHOLD) and \
           math.isclose(Object.scale[1], 1, abs_tol=THRESHOLD) and \
           math.isclose(Object.scale[2], 1, abs_tol=THRESHOLD)


def IsRotationApplied(Object: bpy.types.Object):
    return math.isclose(Object.rotation_euler[0], 0, abs_tol=THRESHOLD) and \
           math.isclose(Object.rotation_euler[1], 0, abs_tol=THRESHOLD) and \
           math.isclose(Object.rotation_euler[2], 0, abs_tol=THRESHOLD)


#Utils check manifold, main function
def is_vertex_manifold(obj, select=False):
    """Retourne les indices des sommets non-manifold de l’objet, tout en restaurant le mode initial."""

    if bpy.context.object :
        bpy.ops.object.mode_set(mode='OBJECT')
        old_obj = bpy.context.object
        bpy.context.view_layer.objects.active = None
        old_obj.select_set(False)
        
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')

    bm = bmesh.from_edit_mesh(obj.data)
    non_manifold_verts = [v for v in bm.verts if v.link_edges and not v.is_manifold]
    indices = [v.index for v in non_manifold_verts]

    if select :
        for v in bm.verts:
            v.select_set(v.index in indices)

        bpy.context.tool_settings.mesh_select_mode[:] = (True, False, False)
        bm.select_mode = {'VERT'}
        bm.select_flush_mode()
        
        bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=False)

    else:
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.view_layer.objects.active = None
        obj.select_set(False)
    
    return indices
