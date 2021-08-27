import bpy
from .. import constants


def base_poll(context):
    """ basic poll function for all lp panels """
    return context.active_object and context.active_object.type == "MESH"


def draw_lp_group(layout, group_node, inp_offset = 1):
    """ draws the given node group as an lp group, for example a mask """
    for i, inp in enumerate(group_node.inputs):
        if i >= inp_offset:
            layout.prop(inp, "default_value", text=inp.name)

    for node in group_node.node_tree.nodes:
        if node.bl_idname == constants.NODES["RAMP"]:
            layout.template_color_ramp(node, "color_ramp", expand=False)
        elif node.bl_idname == constants.NODES["CURVES"]:
            layout.template_curve_mapping(node, "mapping", type='COLOR')