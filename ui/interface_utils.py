import bpy


def base_poll(context):
    """ basic poll function for all lp panels """
    return context.active_object and context.active_object.type == "MESH"