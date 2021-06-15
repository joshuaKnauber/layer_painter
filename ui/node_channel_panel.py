import bpy
from . import interface_utils
from .. import utils


class LP_PT_NodeChannels(bpy.types.Panel):
    bl_idname = "LP_PT_NodeChannels"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Layer Painter"
    bl_label = "Node Channels"
    bl_order = 1
    
    @classmethod
    def poll(cls, context):
        ntree = context.space_data.node_tree
        if interface_utils.base_poll(context) and ntree and ntree.bl_idname == "ShaderNodeTree":
            node = ntree.nodes.active
            if ntree == context.active_object.active_material.node_tree:
                if node:
                    if hasattr(node, "node_tree") and node.node_tree.uid:
                        return False
                    return True
        return False

    def draw(self, context):
        layout = self.layout
        mat = utils.get_active_material(context)
        node = context.space_data.node_tree.nodes.active

        if not mat.lp.has_faulty_layers:
            col = layout.column(align=True)
            col.scale_y = 1.2
            
            for inp in node.inputs:
                if inp.bl_rna.identifier in ["NodeSocketFloat", "NodeSocketFloatFactor", "NodeSocketColor"]:
                    if inp.uid:
                        channel = utils.get_active_material(context).lp.channel_by_inp(inp)
                        row = col.row(align=True)
                        
                        op = row.operator("lp.remove_channel", text="", icon="REMOVE")
                        op.material = utils.get_active_material(context).name
                        op.node = node.name
                        op.input = inp.name
                        
                        row.prop(channel, "default_enable", text="", icon="PINNED" if channel.default_enable else "UNPINNED")
                        row.prop(channel, "name", text="")
                        
                    else:
                        op = col.operator("lp.make_channel", text=f"{inp.name} channel", icon="ADD")
                        op.material = utils.get_active_material(context).name
                        op.node = node.name
                        op.input = inp.name
        else:
            layout.label(text="You material has faulty layers!", icon="ERROR")