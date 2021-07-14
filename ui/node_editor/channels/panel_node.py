import bpy

from layer_painter import utils
from layer_painter.ui import utils_ui


class LP_PT_NodeChannels(bpy.types.Panel):
    bl_idname = "LP_PT_NodeChannels"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Layer Painter"
    bl_label = "Node Channels"
    bl_order = 1
    
    @classmethod
    def poll(cls, context):
        ntree = context.space_data.edit_tree
        if utils_ui.base_poll(context) and \
            ntree and \
            ntree.bl_idname == "ShaderNodeTree" and \
            ntree == context.active_object.active_material.node_tree:
                if ntree.nodes.active:
                    if hasattr(ntree.nodes.active, "node_tree") and \
                        ntree.nodes.active.node_tree.uid:
                        return False
                    return True
        return False

    def draw(self, context):
        layout = self.layout
        mat = utils.active_material(context)
        node = context.space_data.node_tree.nodes.active

        col = layout.column(align=True)
        col.scale_y = 1.2
        
        # draw all valid node inputs
        for inp in node.inputs:
            if inp.bl_rna.identifier in ["NodeSocketFloat", "NodeSocketFloatFactor", "NodeSocketColor"]:

                # draw normal input
                if not inp.uid:
                    
                    # make channel button
                    op = col.operator("lp.make_channel", text=f"{inp.name} channel", icon="ADD")
                    op.material = utils.active_material(context).name
                    op.node = node.name
                    op.input = inp.name
                    
                # draw input that is a channel
                else:
                    channel = utils.active_material(context).lp.channel_by_inp(inp)
                    row = col.row(align=True)
                    
                    # remove channel
                    op = row.operator("lp.remove_channel", text="", icon="REMOVE")
                    op.material = utils.active_material(context).name
                    op.node = node.name
                    op.input = inp.name
                    
                    # enable channel by default
                    row.prop(channel, "default_enable", text="", icon="PINNED" if channel.default_enable else "UNPINNED")

                    # channel name
                    row.prop(channel, "name", text="")                        