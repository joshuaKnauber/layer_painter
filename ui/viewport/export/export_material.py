import bpy

from .... import utils
from ....ui import utils_ui


class LP_PT_ExportPanel(bpy.types.Panel):
    bl_idname = "LP_PT_ExportPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Layer Painter"
    bl_label = ""
    bl_order = 3
    bl_options = {"DEFAULT_CLOSED"}
    
    @classmethod
    def poll(cls, context):
        return utils_ui.base_poll(context) and \
            utils.active_material(context) != None and \
            utils.active_material(context).lp.selected

    def draw_header(self, context):
        mat = utils.active_material(context)
        self.layout.label(text=f"Export {mat.name}")

    def draw(self, context):
        mat = utils.active_material(context)
        layout = self.layout