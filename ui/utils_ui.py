import bpy


def base_poll(context):
    """ basic poll function for all lp panels """
    return context.active_object and context.active_object.type == "MESH"


def draw_lp_group(layout, group_node):
    """ draws the given node group as an lp group, for example a mask """
    for inp in group_node.inputs:
        layout.prop(inp, "default_value", text=inp.name)