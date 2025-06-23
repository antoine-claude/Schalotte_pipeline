# check_ui.py
import bpy
import importlib
from . import utils
importlib.reload(utils) 

class VIEW3D_PT_check_panel(bpy.types.Panel):
    bl_label = "Sanity Check"
    bl_idname = "VIEW3D_PT_check_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Sanity'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        icon = 'ERROR' if scene.check_items else 'CHECKMARK'

        for item in scene.check_items:
            header, panel = layout.panel(f"{item.object_name}"+"_id", default_closed=False)
            header.label(text=f"{item.object_name}"), header.label(icon=icon)
            
            if panel:
                box = panel.box()
                if item.vert_mani :
                    row = box.row()
                    row.label(text=f"Vertice no manifold : {item.vert_mani}/{item.vert_count}", icon ="VERTEXSEL")
#                    , item.is_origin, item.is_rot, item.is_scale
                    op = row.operator("object.check_manifold",icon ="RESTRICT_SELECT_OFF")
                    op.target_name = item.object_name
                    op.select_mode = True
                    
                if not item.is_origin :
                    col = box.column()
                    row = col.row()
                    row.label(text="Location invalid", icon = "OBJECT_ORIGIN")
                    
                if not item.is_rot :
                    col = box.column()
                    row = col.row()
                    row.label(text="Rotation invalid", icon = "DRIVER_ROTATIONAL_DIFFERENCE")

                if not item.is_scale :
                    col = box.column()
                    row = col.row()
                    row.label(text="Scale invalid", icon = "FULLSCREEN_ENTER")                    
          
        layout.operator("object.run_check", text="Vérifier tous les objets")