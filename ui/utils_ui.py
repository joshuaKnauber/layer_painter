import bpy
from .. import constants


def base_poll(context):
    """ basic poll function for all lp panels """
    return context.active_object and context.active_object.type == "MESH"


def draw_lp_group(layout, ntree, group_node, inp_offset = 1):
    """ draws the given node group as an lp group, for example a mask """
    # draw all inputs
    for i, inp in enumerate(group_node.inputs):
        if i >= inp_offset:
            row = layout.row(align=True)

            # draw convert to texture input for color sockets
            if inp.bl_idname == constants.SOCKETS["COLOR"]:
                op = row.operator("lp.toggle_texture", text="", emboss=False, icon="SHADING_RENDERED" if len(inp.links) == 0 else "SHADING_TEXTURE")
                op.node_group = ntree.name
                op.node_name = group_node.name
                op.input_index = i
                row.separator()

            # draw input value
            if len(inp.links) == 0:
                row.prop(inp, "default_value", text=inp.name)
            elif inp.links[0].from_node.bl_idname == constants.NODES["TEX"]:
                draw_texture_input(row, inp.links[0].from_node, ntree=ntree, name=inp.name, icon_only=True, edit_mapping=True)

    # draw special nodes
    for node in group_node.node_tree.nodes:
        if node.bl_idname == constants.NODES["RAMP"] and not node.hide:
            layout.template_color_ramp(node, "color_ramp", expand=False)
        elif node.bl_idname == constants.NODES["CURVES"] and not node.hide:
            layout.template_curve_mapping(node, "mapping", type='COLOR')


def draw_texture_input(layout, tex_node, channel=None, ntree=None, name="", icon_only=False, edit_mapping=False):
    """ draws a row for the given tex node including the painting options """
    if tex_node:
        if name:
            if not tex_node.image:
                layout.template_ID(tex_node, "image", new="image.new", open="image.open", text=name, live_icon=True)
            else:
                layout.template_ID(tex_node, "image", text=name, live_icon=True)
        else:
            if not tex_node.image:
                layout.template_ID(tex_node, "image", new="image.new", open="image.open", live_icon=True)
            else:
                layout.template_ID(tex_node, "image", live_icon=True)

    row = layout.row(align=True)
    if tex_node and tex_node.image and ntree and edit_mapping:
        op = row.operator("lp.image_mapping", text="", icon="ORIENTATION_LOCAL")
        op.node_group = ntree.name
        op.node_name = tex_node.name
        row.separator()

    if bpy.context.mode == "PAINT_TEXTURE" and bpy.context.scene.tool_settings.image_paint.canvas == tex_node.image:
        row.operator("lp.stop_painting", icon="CHECKMARK", text="Finish" if not icon_only else "")
    else:
        if channel:
            op = row.operator("lp.paint_channel", icon="BRUSH_DATA", text="Paint" if not icon_only else "")
            op.channel = channel
        else:
            op = row.operator("lp.paint_channel", icon="BRUSH_DATA", text="Paint" if not icon_only else "")
            op.node_group = ntree.name
            op.node_name = tex_node.name