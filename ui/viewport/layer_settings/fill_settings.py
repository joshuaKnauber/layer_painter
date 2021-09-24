import bpy

from ... import utils_ui
from .... import constants
from ....data.materials.layers.layer_types import layer_fill


def draw_fill(layout, context, mat, layer):
    draw_mapping(layout, context, layer)
    layout.separator(factor=1)
    
    # channel settings
    for channel in mat.lp.channels:
        channel_mix = layer_fill.get_channel_mix_node(layer, channel.uid)
        draw_fill_channel(layout, mat, layer, channel, channel_mix)


def draw_fill_channel(layout, mat, layer, channel, channel_mix):
    box = layout.box()
    row = box.row(align=True)
    
    # enable/disable channel
    hide_icon = "CHECKBOX_DEHLT" if channel_mix.mute else "CHECKBOX_HLT"
    row.prop(channel_mix, "mute", text="", invert_checkbox=True, icon=hide_icon, emboss=False)
    
    # channel name
    split = row.split(factor=0.45)
    split.label(text=channel.name)
    
    # draw channel settings
    if not channel_mix.mute:
        row = split.row()
        
        # channel blending mode
        row.prop(channel_mix, "blend_type", text="", emboss=False)

        # channel opacity
        row.prop(layer_fill.get_channel_opacity_socket(layer, channel.uid), "default_value", text="", slider=True)

        # draw channel data settings
        row = box.row(align=True)
        data_type = layer_fill.get_channel_data_type(layer, channel.uid)

        # channel data type cycle button
        data_icon = "SHADING_RENDERED" if data_type == "COL" else "SHADING_TEXTURE"
        op = row.operator("lp.cycle_channel_data", text="", icon=data_icon, emboss=False)
        op.material = mat.name
        op.layer_uid = layer.uid
        op.channel_uid = channel.uid
        row.separator()

        
        # channel color value
        split = row.split(factor=0.7)
        value_node = layer_fill.get_channel_value_node(layer, channel.uid)
        if data_type == "COL":

            if value_node.bl_idname == constants.NODES["RGB"]:
                split.prop(value_node.outputs[0], "default_value", text="")
            else:
                split.prop(value_node.inputs[0], "default_value", text="", slider=True)

        utils_ui.draw_texture_input(split, value_node if data_type == "TEX" else None, ntree=layer.node.node_tree, channel=channel.uid, non_color=channel.is_data)


def draw_mapping(layout, context, layer):
    box = layout.box()
    row = box.row()
    
    # expand mapping
    expand_icon = "TRIA_DOWN" if context.scene.lp.expand_mapping else "TRIA_RIGHT"
    row.prop(context.scene.lp, "expand_mapping", text="", emboss=False, icon=expand_icon)
    
    # mapping type dropdown
    row.prop(layer, "tex_coords", text="")

    # mapping settings
    if context.scene.lp.expand_mapping:

        # box blend
        if layer.tex_coords == "BOX":
            row.prop(layer, "tex_blend", slider=True)

        row = box.row()
        
        # loc/rot/scale mapping
        col = row.column()
        col.prop(layer, "tex_location")
        col = row.column()
        col.prop(layer, "tex_rotation")
        col = row.column()
        col.prop(layer, "tex_scale")
