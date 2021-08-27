import bpy

from .... import utils, constants
from ....ui import utils_ui
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
        layout.prop(mat.lp, "channel", text="")

        # draw mask add
        row = layout.row()
        row.scale_y = 1.2
        row.operator("lp.add_mask", icon="ADD")

        # draw mask stack
        for group_node in layer.get_mask_nodes(mat.lp.channel):
            box = layout.box()

            # draw mask header
            row = box.row()
            row.prop(group_node, "hide", text="", icon="DISCLOSURE_TRI_RIGHT" if group_node.hide else "DISCLOSURE_TRI_DOWN", emboss=False)
            row.prop(group_node, "mute", text="", icon="HIDE_ON" if group_node.mute else "HIDE_OFF", emboss=False)
            row.prop(group_node, "label", text="")

            # draw mask blend options
            if constants.MIX_MASK in group_node.node_tree.nodes:
                subrow = row.row()
                subrow.prop(group_node.node_tree.nodes[constants.MIX_MASK], "blend_type", text="", emboss=False)
                subrow.prop(group_node.node_tree.nodes[constants.MIX_MASK].inputs[0], "default_value", text="")

            # draw mask move options
            subrow = row.row(align=True)
            subcol = subrow.column(align=True)
            subcol.enabled = not layer.is_group_top_mask(group_node, mat.lp.channel)
            op = subcol.operator("lp.move_mask", text="", icon="TRIA_UP")
            op.node_name = group_node.name
            op.move_up = True

            subcol = subrow.column(align=True)
            subcol.enabled = not layer.is_group_bottom_mask(group_node, mat.lp.channel)
            op = subcol.operator("lp.move_mask", text="", icon="TRIA_DOWN")
            op.node_name = group_node.name
            op.move_up = False

            # draw mask remove
            row.operator("lp.remove_mask", text="", emboss=False, icon="PANEL_CLOSE").node_name = group_node.name

            # draw group inputs
            if not group_node.hide:
                utils_ui.draw_lp_group(box, group_node)