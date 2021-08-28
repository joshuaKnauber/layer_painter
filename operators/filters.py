import bpy

from .. import utils
from ..operators import utils_operator


class LP_OT_AddFilter(bpy.types.Operator):
    bl_idname = "lp.add_filter"
    bl_label = "Add Filter"
    bl_description = "Adds a filter"
    bl_options = {"REGISTER", "INTERNAL"}
    
    @classmethod
    def poll(cls, context):
        mat = utils.active_material(context)
        return utils_operator.base_poll(context) and mat.lp.selected

    def get_selected_asset(self, context):
        index = int(context.scene.lp.filters)
        return context.scene.lp.filter_assets[index]

    def execute(self, context):
        if len(context.scene.lp.filter_assets) > 0:
            utils.active_material(context).lp.selected.add_filter( self.get_selected_asset(context) )
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout

        if len(context.scene.lp.filter_assets) > 0:
            box = layout.box()
            col = box.column(align=True)
            col.template_icon_view(context.scene.lp, "filters", show_labels=True, scale=7)
            row = col.row()
            row.label(text=self.get_selected_asset(context).name)
        else:
            layout.label(text="No assets. Add a file in the preferences.", icon="ERROR")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)