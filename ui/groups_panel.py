import bpy
from . import interface_utils


def group_panel_poll(context):
    ntree = context.space_data.node_tree
    if interface_utils.base_poll(context) and ntree and ntree.bl_idname == "ShaderNodeTree":
        if ntree == context.active_object.active_material.node_tree:
            return ntree.nodes.active and hasattr(ntree.nodes.active, "node_tree") and ntree.nodes.active.node_tree
    return False


class LP_PT_Groups(bpy.types.Panel):
    bl_idname = "LP_PT_Groups"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Layer Painter"
    bl_label = "LP Groups"
    bl_order = 2
    
    @classmethod
    def poll(cls, context):
        return group_panel_poll(context)

    def draw(self, context):
        layout = self.layout
        node = context.space_data.node_tree.nodes.active
        group_stngs = node.node_tree.lp_group
        
        if not group_stngs.is_mask:
            row = layout.row()
            row.scale_y = 1.5
            row.prop(group_stngs, "is_mask", toggle=True, text="Turn into mask", icon="CHECKMARK")
            
        elif group_stngs.is_mask:
            row = layout.row()
            row.scale_y = 1.5
            row.prop(group_stngs, "is_mask", toggle=True, text="Disable mask", icon="PANEL_CLOSE", invert_checkbox=True)

            row = layout.row()
            row.scale_y = 1.2
            if context.space_data.edit_tree == context.active_object.active_material.node_tree:
                row.operator("node.group_edit", text="Edit group", icon="GREASEPENCIL")
            else:
                row.operator("node.group_edit", text="Stop editing", icon="GREASEPENCIL")
            
            layout.separator()
            
            box = layout.box()
            box.label(text="Thumbnail")
            box.template_ID(group_stngs, "thumbnail", new="image.new", open="image.open")

            layout.separator()

            self.draw_input_settings(layout, node.node_tree)
            

    def draw_input_settings(self, layout, ntree):
        for inp in ntree.inputs:
            
            box = layout.box()
            row = box.row(align=True)
            row.prop(inp.lp_group,"mode", text="", icon_only=True)
            row.prop(inp, "name", text="")
            
            if inp.lp_group.mode == "INPUT":
                row = box.row()
                row.prop(inp, "default_value", text="Default")

                if hasattr(inp, "min_value"):
                    row = row.row(align=True)
                    row.prop(inp, "min_value", text="Min")
                    row.prop(inp, "max_value", text="Max")
            
            
class LP_PT_GroupPreview(bpy.types.Panel):
    bl_idname = "LP_PT_GroupPreview"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Layer Painter"
    bl_label = ""
    bl_order = 3
    bl_options = {"DRAW_BOX"}
    
    @classmethod
    def poll(cls, context):
        if group_panel_poll(context):
            return context.space_data.node_tree.nodes.active.node_tree.lp_group.is_mask
        return False
    
    def draw_header(self, context):
        self.layout.label(text=f"{context.space_data.node_tree.nodes.active.node_tree.name} UI Preview")

    def draw(self, context):
        layout = self.layout
        node = context.space_data.node_tree.nodes.active
        group_stngs = node.node_tree.lp_group
        
        if group_stngs.is_mask:
            interface_utils.draw_lp_group(layout, node, True)