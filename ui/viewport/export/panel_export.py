import bpy

from .... import utils
from ....ui import utils_ui
from ....operators import baking


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
        self.layout.label(text="WIP - ONLY UI NO FUNCTIONALITY", icon="ERROR")
        if baking.is_baking():
            self.draw_bake_queue(context)
        else:
            self.draw_baking_settings(context)

    def draw_bake_queue(self, context):
        mat = utils.active_material(context)
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        for channel in mat.lp.channels:
            if channel.bake:
                if channel.completed_bake:
                    layout.label(text=channel.name, icon="CHECKMARK")
                else:
                    layout.label(text=channel.name, icon="REMOVE")

    def draw_baking_settings(self, context):
        mat = utils.active_material(context)
        layout = self.layout
        layout.prop(context.scene.lp.export, "directory", text="")

        # draw channels to include in baking
        col = layout.column(heading="Channels")
        col.use_property_split = True
        col.use_property_decorate = False

        subcol = col.column(align=True)
        for channel in mat.lp.channels:
            subcol.prop(channel, "bake", text=channel.name, toggle=True)
        col.separator()

        subcol = col.column(align=True)
        subcol.prop(context.scene.lp.export, "resolution")
        subcol.prop(context.scene.render.bake, "margin")
        col.prop(context.scene.lp.export, "base_color")
        col.prop(context.scene.render.image_settings, "file_format")
        
        layout.separator()

        row = layout.row()
        row.scale_y = 1.5
        row.operator("lp.bake_modal", text="Bake and Export", icon="RENDER_STILL")