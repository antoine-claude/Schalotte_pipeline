
import bpy
import math
import bmesh
from mathutils import Vector

THRESHOLD = 0.001
state_dict = {}
def unhide(obj: bpy.types.Object):
    if obj.name not in state_dict:
        state_dict[obj.name] = {
            "eye": obj.hide_get(),
            "view": obj.hide_viewport
        }

    obj.hide_set(False)
    obj.hide_viewport = False

    return state_dict[obj.name]["eye"], state_dict[obj.name]["view"]

def rehide(obj: bpy.types.Object):
    if (state := state_dict.pop(obj.name, None)):
        obj.hide_set(state["eye"])
        obj.hide_viewport = state["view"]
        
def select_function(obj: bpy.types.Object):
    unhide(obj)
    if bpy.context.object: 
        old_obj = bpy.context.object
        bpy.context.view_layer.objects.active = old_obj
        bpy.ops.object.mode_set(mode='OBJECT')
        old_obj.select_set(False)
        bpy.context.view_layer.objects.active = None

    for o in bpy.context.selected_objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.context.view_layer.update()

def is_object_in_collection_and_subcollections(obj: bpy.types.Object, coll):
    collections_to_check = [coll] + list(coll.children_recursive)   
    for c in collections_to_check:
        if obj.name in c.objects:
            return True
    return False

def print_all_defined_properties(item):
    print(f"--- {item.object_name} ---")
    for prop_id in item.bl_rna.properties.keys():
        if prop_id in {"rna_type"}:
            continue
        val = getattr(item, prop_id)
        print(f"{prop_id} = {val}")

def remove_empty_check_items(scene):
    items = scene.check_items
    for i in reversed(range(len(items))):
        item = items[i]
        is_empty = True
        for prop_id in item.bl_rna.properties.keys():
            if prop_id in {"rna_type", "object_name"}:
                continue
            val = getattr(item, prop_id)
            if val not in (0, 0.0, "", None, False):
                is_empty = False
                break
        if is_empty:
            items.remove(i)

def IsInCollection(Object: bpy.types.Object):
    for obj in Object.users_collection :
        if not obj in bpy.data.collections[:] :
            break
        else :
            return not obj in bpy.data.collections[:]


def IsOnWorldOrigin(obj: bpy.types.Object):
    return math.isclose(obj.location[0], 0, abs_tol=THRESHOLD) and \
           math.isclose(obj.location[1], 0, abs_tol=THRESHOLD) and \
           math.isclose(obj.location[2], 0, abs_tol=THRESHOLD)

def IsScaleApplied(obj: bpy.types.Object):
    return math.isclose(obj.scale[0], 1, abs_tol=THRESHOLD) and \
           math.isclose(obj.scale[1], 1, abs_tol=THRESHOLD) and \
           math.isclose(obj.scale[2], 1, abs_tol=THRESHOLD)

def IsRotationApplied(obj: bpy.types.Object):
    return math.isclose(obj.rotation_euler[0], 0, abs_tol=THRESHOLD) and \
           math.isclose(obj.rotation_euler[1], 0, abs_tol=THRESHOLD) and \
           math.isclose(obj.rotation_euler[2], 0, abs_tol=THRESHOLD)

def is_animated(obj: bpy.types.Object) :
    anim = obj.animation_data
    print("test check anim")
    if anim:
        has_action = anim.action is not None
        has_drivers = len(anim.drivers) > 0
        has_nla = any(len(t.strips) > 0 for t in anim.nla_tracks)

        if not (has_action or has_drivers or has_nla):
            obj.animation_data_clear()
            print("Bloc animation_data présent mais totalement vide et inutile.")
            return False
        else:
            print("Bloc animation_data contient encore des données utiles.")
            return True
    else : 
        return False



def is_vertex_manifold(obj: bpy.types.Object, select=False):
    if obj.type != 'MESH':
        return []

    if select:
        select_function(obj)
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(obj.data)
    else:
        depsgraph = bpy.context.evaluated_depsgraph_get()
        obj_eval = obj.evaluated_get(depsgraph)
        mesh = obj_eval.to_mesh()
        bm = bmesh.new()
        bm.from_mesh(mesh)

    non_manifold_verts = [v for v in bm.verts if v.link_edges and not v.is_manifold]
    indices = [v.index for v in non_manifold_verts]

    if select:
        for v in bm.verts:
            v.select_set(v.index in indices)
        bpy.context.tool_settings.mesh_select_mode[:] = (True, False, False)
        bm.select_mode = {'VERT'}
        bm.select_flush_mode()
        bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=False)
    else:
        bm.free()
        obj_eval.to_mesh_clear()

    return indices

def is_vertex_overlap(obj: bpy.types.Object, threshold=1e-5, select=False):
    if obj.type != 'MESH':
        return []

    if select:
        select_function(obj)
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(obj.data)
    else:
        depsgraph = bpy.context.evaluated_depsgraph_get()
        obj_eval = obj.evaluated_get(depsgraph)
        mesh = obj_eval.to_mesh()
        bm = bmesh.new()
        bm.from_mesh(mesh)

    # Use spatial hashing for faster lookup
    hash_map = {}
    overlapping_verts = set()
    for v in bm.verts:
        key = (round(v.co.x / threshold), round(v.co.y / threshold), round(v.co.z / threshold))
        if key in hash_map:
            overlapping_verts.add(v)
            overlapping_verts.add(hash_map[key])
        else:
            hash_map[key] = v

    indices = [v.index for v in overlapping_verts]

    if select:
        for v in bm.verts:
            v.select = False
        for v in overlapping_verts:
            v.select = True
        bpy.context.tool_settings.mesh_select_mode[:] = (True, False, False)
        bm.select_mode = {'VERT'}
        bm.select_flush_mode()
        bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=False)
    else:
        bm.free()
        obj_eval.to_mesh_clear()

    return indices

def flip_face_if_not_contiguous(obj: bpy.types.Object, select=False, flip=False):
    if obj.type != 'MESH':
        return 0

    if select or flip:
        select_function(obj)
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(obj.data)
    else:
        depsgraph = bpy.context.evaluated_depsgraph_get()
        obj_eval = obj.evaluated_get(depsgraph)
        mesh = obj_eval.to_mesh()
        bm = bmesh.new()
        bm.from_mesh(mesh)

    bm.normal_update()
    normal_count = 0
    passages = {}
    candidate_faces = set()

    for edge in bm.edges:
        if edge.is_manifold and not edge.is_contiguous:
            for face in edge.link_faces:
                passages[face] = passages.get(face, 0) + 1
                if passages[face] == len(face.edges) - 1:
                    normal_count += 1
                    candidate_faces.add(face)

    if select or flip:
        for face in candidate_faces:
            face.select_set(True)
            if flip:
                face.normal_flip()
        bpy.context.tool_settings.mesh_select_mode[:] = (False, False, True)
        bm.select_mode = {'FACE'}
        bm.select_flush_mode()
        bmesh.update_edit_mesh(obj.data)
    else:
        bm.free()
        obj_eval.to_mesh_clear()

    return normal_count

def is_polygon_valid(obj: bpy.types.Object, select=False, type="tri"):
    if obj.type != 'MESH':
        return 0

    if select:
        select_function(obj)
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(obj.data)
    else:
        depsgraph = bpy.context.evaluated_depsgraph_get()
        obj_eval = obj.evaluated_get(depsgraph)
        mesh = obj_eval.to_mesh()
        bm = bmesh.new()
        bm.from_mesh(mesh)

    tri_count = 0
    ngone_count = 0
    tri_faces = []
    ngone_faces = []

    for face in bm.faces:
        n_edges = len(face.edges)
        if n_edges == 3:
            tri_count += 1
            tri_faces.append(face)
        elif n_edges > 4:
            ngone_count += 1
            ngone_faces.append(face)

    if select:
        target_faces = tri_faces if type == 'tri' else ngone_faces
        for face in target_faces:
            face.select_set(True)
        bpy.context.tool_settings.mesh_select_mode[:] = (False, False, True)
        bm.select_mode = {'FACE'}
        bm.select_flush_mode()
        bmesh.update_edit_mesh(obj.data)
    else:
        bm.free()
        obj_eval.to_mesh_clear()

    return tri_count if type == 'tri' else ngone_count

def has_uv_overlap(obj: bpy.types.Object):
    if obj.type != 'MESH':
        return False

    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    mesh = obj_eval.to_mesh()

    bm = bmesh.new()
    bm.from_mesh(mesh)
    uv_layer = bm.loops.layers.uv.active

    if not uv_layer:
        bm.free()
        obj_eval.to_mesh_clear()
        return False

    def tri_overlap_2d(a1, a2, a3, b1, b2, b3):
        def edge(p1, p2): return p2 - p1
        def perp(v): return Vector((-v.y, v.x))
        def project(tri, axis):
            dots = [v.dot(axis) for v in tri]
            return min(dots), max(dots)
        def separating_axis(tri1, tri2):
            for i in range(3):
                axis = perp(edge(tri1[i], tri1[(i + 1) % 3])).normalized()
                min1, max1 = project(tri1, axis)
                min2, max2 = project(tri2, axis)
                if max1 < min2 or max2 < min1:
                    return True
            return False
        if any((Vector(v1) - Vector(v2)).length < 1e-5 for v1 in (a1, a2, a3) for v2 in (b1, b2, b3)):
            return False
        if separating_axis([a1, a2, a3], [b1, b2, b3]):
            return False
        if separating_axis([b1, b2, b3], [a1, a2, a3]):
            return False
        return True

    def aabb_overlap(a1, a2, a3, b1, b2, b3):
        ax = [a1.x, a2.x, a3.x]
        ay = [a1.y, a2.y, a3.y]
        bx = [b1.x, b2.x, b3.x]
        by = [b1.y, b2.y, b3.y]
        return not (max(ax) < min(bx) or max(bx) < min(ax) or
                    max(ay) < min(by) or max(by) < min(ay))

    triangles = []
    for face in bm.faces:
        uvs = [loop[uv_layer].uv.copy() for loop in face.loops]
        if len(uvs) < 3:
            continue
        for i in range(1, len(uvs) - 1):
            triangles.append((uvs[0], uvs[i], uvs[i + 1]))

    for i, tri_a in enumerate(triangles):
        for j in range(i + 1, len(triangles)):
            tri_b = triangles[j]
            if not aabb_overlap(*tri_a, *tri_b):
                continue
            if tri_overlap_2d(*tri_a, *tri_b):
                bm.free()
                obj_eval.to_mesh_clear()
                return True

    bm.free()
    obj_eval.to_mesh_clear()
    return False
