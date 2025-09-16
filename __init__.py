
bl_info = {
    "name": "Check Scene STM",
    "author": "Antoine CLAUDE",
    "description": "Blender addon to check Scene",
    "blender": (4, 5, 2),
    "version": (0, 1, 0),
}
import bpy
import importlib
from . import addon_updater_ops


@addon_updater_ops.make_annotations
class DemoPreferences(bpy.types.AddonPreferences):
	"""Demo bare-bones preferences"""
	bl_idname = __package__

	# Addon updater preferences.

	auto_check_update = bpy.props.BoolProperty(
		name="Auto-check for Update",
		description="If enabled, auto-check for updates using an interval",
		default=False)

	updater_interval_months = bpy.props.IntProperty(
		name='Months',
		description="Number of months between checking for updates",
		default=0,
		min=0)

	updater_interval_days = bpy.props.IntProperty(
		name='Days',
		description="Number of days between checking for updates",
		default=7,
		min=0,
		max=31)

	updater_interval_hours = bpy.props.IntProperty(
		name='Hours',
		description="Number of hours between checking for updates",
		default=0,
		min=0,
		max=23)

	updater_interval_minutes = bpy.props.IntProperty(
		name='Minutes',
		description="Number of minutes between checking for updates",
		default=0,
		min=0,
		max=59)

	def draw(self, context):
		layout = self.layout

		# Works best if a column, or even just self.layout.
		mainrow = layout.row()
		col = mainrow.column()

		# Updater draw function, could also pass in col as third arg.
		addon_updater_ops.update_settings_ui(self, context)

		# Alternate draw function, which is more condensed and can be
		# placed within an existing draw function. Only contains:
		#   1) check for update/update now buttons
		#   2) toggle for auto-check (interval will be equal to what is set above)
		# addon_updater_ops.update_settings_ui_condensed(self, context, col)

		# Adding another column to help show the above condensed ui as one column
		# col = mainrow.column()
		# col.scale_y = 2
		# ops = col.operator("wm.url_open","Open webpage ")
		# ops.url=addon_updater_ops.updater.website


# Register les classes dynamiquement
classes = []

def register():
	from . import ops, panel_ui
	importlib.reload(ops)
	importlib.reload(panel_ui)

	addon_updater_ops.register(bl_info)

	global classes
	classes = (
        DemoPreferences,
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
		addon_updater_ops.make_annotations(cls)  # Avoid blender 2.8 warnings.
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
	addon_updater_ops.unregister()
	
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
