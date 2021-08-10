import bpy

from .... import utils
from ....ui import utils_ui


class LP_PT_LayerPanel(bpy.types.Panel):
    bl_idname = "LP_PT_LayerPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Layer Painter"
    bl_label = ""
    bl_order = 1
    bl_options = {"HEADER_LAYOUT_EXPAND"}
    
    @classmethod
    def poll(cls, context):
        return utils_ui.base_poll(context) and \
            utils.active_material(context) != None

    def draw_header(self, context):
        mat = utils.active_material(context)

        # material panel title
        self.layout.label(text=f"{mat.name} Layers")

        # preview settings
        if len(mat.lp.channels):
            row = self.layout.row(align=True)
            row.alignment = "RIGHT"
            row.prop(mat.lp, "use_preview", text="", icon="GHOST_ENABLED")
            
            if mat.lp.use_preview:
                row.prop(mat.lp, "preview_channel", text="")
        
    def draw_operators(self, layout, mat):
        box = layout.box()
        row = box.row()
        
        # add layer operators
        sub_row = row.row(align=False)
        sub_row.operator("lp.add_fill_layer", text="", icon="FILE_NEW", emboss=False).material = mat.name

        # move layer operators
        sub_row = row.row(align=False)
        sub_row.alignment = "CENTER"
        sub_row.operator("lp.move_layer_up", text="", icon="TRIA_UP", emboss=False).material = mat.name
        sub_row.operator("lp.move_layer_down", text="", icon="TRIA_DOWN", emboss=False).material = mat.name

        # remove layer operator
        sub_row = row.row(align=False)
        sub_row.alignment = "RIGHT"
        sub_row.operator("lp.remove_layer", text="", icon="TRASH", emboss=False).material = mat.name

    def draw(self, context):
        mat = utils.active_material(context)
        layout = self.layout
        col = layout.column(align=True)
        
        self.draw_operators(col, mat)
        
        # draw layer list
        row = col.row(align=True)
        row.scale_y = 1.25
        row.template_list("LP_UL_Layers", "material_layers",
                            mat.lp, "layers",
                            mat.lp, "selected_index",rows=3,sort_reverse=True)
        
        # no layers info
        if len(mat.lp.layers) == 0:
            col.label(text="No layers added", icon="INFO")
            
            # no channels info
            if len(mat.lp.channels) == 0:
                # pbr setup button
                layout.separator()
                row = layout.row()
                row.scale_y = 1.5
                row.operator("lp.pbr_setup", icon="ADD").material = mat.name

                # switch to node editor button
                layout.operator("lp.switch_to_node_editor", icon="WINDOW", text="Edit custom channels")
