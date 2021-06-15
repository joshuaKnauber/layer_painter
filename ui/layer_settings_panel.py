import bpy
from . import interface_utils
from .. import utils


class LP_PT_LayerSettingsPanel(bpy.types.Panel):
    bl_idname = "LP_PT_LayerSettingsPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Layer Painter"
    bl_label = ""
    bl_order = 2
    
    @classmethod
    def poll(cls, context):
        mat = utils.get_active_material(context)
        if interface_utils.base_poll(context) and mat != None:
            if mat.lp.active != None:
                return (not mat.lp.has_faulty_layers) and (not mat.lp.has_faulty_channels)
        return False

    def draw_header(self, context):
        self.layout.label(text=f"{context.active_object.active_material.lp.active.node.label} Settings")

    def draw_channel(self, layout, layer, channel, channel_mix):
        box = layout.box()
        row = box.row(align=True)
        
        hide_icon = "CHECKBOX_DEHLT" if channel_mix.mute else "CHECKBOX_HLT"
        row.prop(channel_mix, "mute", text="", invert_checkbox=True, icon=hide_icon, emboss=False)
        
        split = row.split(factor=0.45)
        split.label(text=channel.name)
        
        if not channel_mix.mute:
            row = split.row()
            row.prop(channel_mix, "blend_type", text="", emboss=False)
            row.prop(layer.get_channel_opacity_socket( channel.uid ), "default_value", text="", slider=True)

            row = box.row()
            row.prop(layer.get_channel_value_socket( channel.uid ), "default_value", text="", slider=True)

    def draw(self, context):
        layout = self.layout
        mat = utils.get_active_material(context)
        layer = mat.lp.active
        
        for channel in mat.lp.channels:
            channel_mix = layer.get_channel_node( channel.uid )
            self.draw_channel(layout, layer, channel, channel_mix)
                
        if len(mat.lp.channels) == 0:
            row = layout.row()
            row.scale_y = 1.5
            row.operator("lp.pbr_setup", icon="ADD").material = mat.name
            layout.operator("lp.switch_to_node_editor", icon="WINDOW", text="Edit custom channels")