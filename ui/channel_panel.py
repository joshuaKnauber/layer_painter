import bpy
from . import interface_utils
from .. import utils


class LP_PT_Channels(bpy.types.Panel):
    bl_idname = "LP_PT_Channels"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Layer Painter"
    bl_label = "Material Channels"
    bl_order = 0
    
    @classmethod
    def poll(cls, context):
        ntree = context.space_data.node_tree
        if interface_utils.base_poll(context) and ntree and ntree.bl_idname == "ShaderNodeTree":
            return ntree == context.active_object.active_material.node_tree
        return False

    def draw(self, context):
        layout = self.layout
        mat = utils.get_active_material(context)

        if not mat.lp.has_faulty_layers:
            col = layout.column(align=True)
            col.scale_y = 1.2
            
            for channel in mat.lp.channels:            
                row = col.row(align=True)
                
                if channel.inp:
                    op = row.operator("lp.remove_channel", text="", icon="REMOVE")
                    op.material = mat.name
                    op.node = channel.inp.node.name
                    op.input = channel.inp.name
                    
                    row.prop(channel, "default_enable", text="", icon="PINNED" if channel.default_enable else "UNPINNED")
                    row.prop(channel, "name", text="")
                    
                    sub_col = row.column(align=True)
                    sub_col.enabled = channel != mat.lp.channels[0]
                    op = sub_col.operator("lp.move_channel_up", text="", icon="TRIA_UP")
                    op.material = mat.name
                    op.channel_uid = channel.uid

                    sub_col = row.column(align=True)
                    sub_col.enabled = channel != mat.lp.channels[-1]
                    op = sub_col.operator("lp.move_channel_down", text="", icon="TRIA_DOWN")
                    op.material = mat.name
                    op.channel_uid = channel.uid
                    
                else:
                    row.alert = True
                    op = row.operator("lp.remove_channel", text="Faulty channel!", icon="TRASH")
                    op.material = mat.name
                    op.overwrite_uid = channel.uid
                
            if len(mat.lp.channels) == 0:
                row = layout.row()
                row.scale_y = 1.5
                row.operator("lp.pbr_setup", icon="ADD").material = mat.name
                
        else:
            layout.label(text="You material has faulty layers!", icon="ERROR")