# check_ui.py
import bpy
import importlib
from . import utils
importlib.reload(utils) 
from . import addon_updater_ops

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

        # Option panel
        option_header, option_panel = layout.panel("OPTION_id", default_closed=False)
        option_header.label(text="OPTION")

        if option_panel:
            option_box = option_panel.box()
            option_box.prop(scene, "checkbox_mani")
            option_box.prop(scene, "checkbox_transform")
            option_box.prop(scene, "checkbox_uv")
            option_box.prop(scene, "checkbox_vert_overlap")
            option_box.prop(scene, "checkbox_normal")
            option_box.prop(scene, "checkbox_ngone")
            option_box.prop(scene, "checkbox_hide")
            option_box.prop(scene, "checkbox_anim")

        # Mesh panel
        mesh_header, mesh_panel = layout.panel("MESH_id", default_closed=True)
        mesh_header.label(text="MESH")

        if mesh_panel:
            for item in scene.check_items:
                box = mesh_panel.box()
                # if utils.is_check_item_empty_except_name(item):continue
                layer, subpanel = box.panel(f"{item.object_name}"+"_id", default_closed=True)
                layer.label(text=f"{item.object_name}"), layer.label(icon=icon)
                
                if subpanel:
                    box = subpanel.box()
                    if item.vert_mani :
                        row = box.row()
                        row.label(text=f"Vertice no manifold : {item.vert_mani}/{item.vert_count}", icon ="VERTEXSEL")

                        op = row.operator("object.select_manifold",icon ="RESTRICT_SELECT_OFF")
                        op.target_name = item.object_name
                        op.select_mode = True
                        
                    if item.is_origin :
                        col = box.column()
                        row = col.row()
                        row.label(text="Location invalid", icon = "OBJECT_ORIGIN")
                        
                    if item.is_rot :
                        col = box.column()
                        row = col.row()
                        row.label(text="Rotation invalid", icon = "DRIVER_ROTATIONAL_DIFFERENCE")

                    if item.is_scale :
                        col = box.column()
                        row = col.row()
                        row.label(text="Scale invalid", icon = "FULLSCREEN_ENTER")                    
            
                    if item.uv_overlap :
                        col = box.column()
                        row = col.row()
                        row.label(text="UV invalid", icon = "UV")           
     
                    if item.vert_overlap :
                        col = box.column()
                        row = col.row()
                        row.label(text="vertex overlapping", icon = "VERTEXSEL")   
                        op = row.operator("object.select_vertices_dupli",icon ="RESTRICT_SELECT_OFF")
                        op.target_name = item.object_name 
                        
                    if item.clean_normal :
                        col = box.column()
                        row = col.row()
                        row.label(text=f"Normal badly oriented : {item.clean_normal}", icon = "NORMALS_FACE") 
                        op = row.operator("object.select_normal",icon ="RESTRICT_SELECT_OFF")
                        op.target_name = item.object_name 

                    if item.is_ngone :
                        col = box.column()
                        row = col.row()
                        row.label(text=f"Ngone : {item.is_ngone}", icon = "NORMALS_FACE") 
                        if item.is_ngone : 
                            op = row.operator("object.select_invalid_poly",icon ="RESTRICT_SELECT_OFF")
                            op.target_name = item.object_name      
                            op.shape = 'ngone'

                    if item.is_tri :
                        col = box.column()
                        row = col.row()
                        row.label(text=f"Trigone : {item.is_tri}", icon = "NORMALS_FACE") 
                        if item.is_tri : 
                            op = row.operator("object.select_invalid_poly",icon ="RESTRICT_SELECT_OFF")
                            op.target_name = item.object_name  
                            op.shape = 'tri'
                    
                    if item.is_hide :
                        col = box.column()
                        row = col.row()
                        row.label(text=f"Item hidden", icon = "HIDE_OFF")

                    if item.is_anim :
                        col = box.column()
                        row = col.row()
                        row.label(text=f"Item animated", icon = "KEYTYPE_KEYFRAME_VEC"),
                        op = row.operator("object.clean_anim", icon="TRASH")
                        op.target_name = item.object_name

        layout.operator("object.run_check", text="Vérifier tous les objets")

        # Vérification des updates en arrière-plan
        addon_updater_ops.check_for_update_background()

        layout.separator()
        layout.label(text="Mises à jour", icon="IMPORT")

        # Si une mise à jour est prête, afficher un message
        if addon_updater_ops.updater.update_ready:
            layout.label(text="Nouvelle mise à jour disponible !", icon="INFO")

        # Boîte UI de l’updater (boutons update/check/etc.)
        addon_updater_ops.update_notice_box_ui(self, context)