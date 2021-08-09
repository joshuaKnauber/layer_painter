import bpy

from layer_painter import utils
from layer_painter.ui import utils_ui
from layer_painter.data.materials.layers.layer_types import layer_fill
from . import fill_settings


class LP_PT_LayerSettingsPanel(bpy.types.Panel):
    bl_idname = "LP_PT_LayerSettingsPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Layer Painter"
    bl_label = ""
    bl_order = 2
    
    @classmethod
    def poll(cls, context):
        mat = utils.active_material(context)
        if utils_ui.base_poll(context) and \
            mat != None:
            return mat.lp.selected != None
        return False

    def draw_header(self, context):
        # layer settings title
        mat = utils.active_material(context)
        self.layout.label(text=f"{ mat.lp.selected.node.label } Settings")

    def draw(self, context):
        layout = self.layout
        mat = utils.active_material(context)
        layer = mat.lp.selected
        
        # draw missing layer group warning
        if not layer.node:
            layout.label(text="Layer is missing it's node!")

        else:
            # no channels info
            if len(mat.lp.channels) == 0:
                
                # pbr setup button
                row = layout.row()
                row.scale_y = 1.5
                row.operator("lp.pbr_setup", icon="ADD").material = mat.name

                # switch to node editor button
                layout.operator("lp.switch_to_node_editor", icon="WINDOW", text="Edit custom channels")
            
            # draw layer settings
            else:
                
                # layer navigation
                row = layout.row()
                row.scale_y = 1.2
                row.prop(context.scene.lp, "layer_nav", expand=True)
                layout.separator(factor=1)
                
                # layer settings
                if context.scene.lp.layer_nav == "LAYER":
                    
                    # draw fill settings
                    if layer.layer_type == "FILL":
                        # layer mapping
                        fill_settings.draw_fill(layout, context, mat, layer)
                            
                    elif layer.layer_type == "PAINT":
                        pass

                # mask settings
                elif context.scene.lp.layer_nav == "MASKS":
                    self.draw_masks(layout, mat, layer)
                
                # filter settings
                elif context.scene.lp.layer_nav == "FILTERS":
                    layout.label(text="Placeholder")
                
                
    def draw_masks(self, layout, mat, layer):
        op = layout.operator("lp.add_mask")
        op.group_name = "Noise"
        op.file_uid = "0be674aaa2"