import bpy
from .. import utils


def base_poll(context):
    """ basic poll function for all lp operators """
    return utils.get_active_material(context) != None


def get_input(material_name, node_name, input_name):
    """ function to get an input from keys. Returns None if not found """
    if material_name in bpy.data.materials:
        if node_name in bpy.data.materials[material_name].node_tree.nodes:
            if input_name in bpy.data.materials[material_name].node_tree.nodes[node_name].inputs:
                return bpy.data.materials[material_name].node_tree.nodes[node_name].inputs[input_name]
    return None