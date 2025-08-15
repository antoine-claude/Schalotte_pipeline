
bl_info = {
    "name": "20STM Tools",
    "author": "Antoine CLAUDE",
    "description": "Blender addon to check Scene",
    "blender": (4, 4, 3),
    "version": (0, 1, 0),
}
import bpy
import importlib


# Register les classes dynamiquement
classes = []

def register():
    from . import ops, panel_ui
    importlib.reload(ops)
    importlib.reload(panel_ui)

    global classes
    classes = (
        ops.CheckItem,
        ops.OBJECT_OT_run_check,
        ops.OBJECT_OT_select_manifold,
        ops.OBJECT_OT_select_vert_dupli,
        ops.OBJECT_OT_select_normal,
        ops.OBJECT_OT_select_invalid_poly,
        ops.OBJECT_OT_clean_anim,
        panel_ui.VIEW3D_PT_check_panel
    )

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.check_items = bpy.props.CollectionProperty(type=ops.CheckItem)
    bpy.types.Scene.checkbox_mani = bpy.props.BoolProperty(name="Check Manifold", default=True)
    bpy.types.Scene.checkbox_transform = bpy.props.BoolProperty(name="Check Transform", default=True)
    bpy.types.Scene.checkbox_uv = bpy.props.BoolProperty(name="Check UV", default=True)
    bpy.types.Scene.checkbox_vert_overlap = bpy.props.BoolProperty(name="Check Vertice Overlap", default=True)
    bpy.types.Scene.checkbox_normal = bpy.props.BoolProperty(name="Check Normal", default=True)
    bpy.types.Scene.checkbox_ngone = bpy.props.BoolProperty(name="Check Ngone", default=True)
    bpy.types.Scene.checkbox_hide = bpy.props.BoolProperty(name="Check Hide", default=True)
    bpy.types.Scene.checkbox_anim = bpy.props.BoolProperty(name="Check Keyframe", default=True)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.check_items
    del bpy.types.Scene.checkbox_mani
    del bpy.types.Scene.checkbox_transform
    del bpy.types.Scene.checkbox_uv
    del bpy.types.Scene.checkbox_normal
    del bpy.types.Scene.checkbox_vert_overlap
    del bpy.types.Scene.checkbox_ngone
    del bpy.types.Scene.checkbox_hide
    del bpy.types.Scene.checkbox_anim
