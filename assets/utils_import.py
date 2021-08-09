import bpy


def get_group(blend_path, name):
    """ imports the group with the given name from the blend file after checking if it already exists """
    if name in bpy.data.node_groups:
        return bpy.data.node_groups[name]
    else:
        __append_group(blend_path, name)
        if name in bpy.data.node_groups:
            return bpy.data.node_groups[name]
    return None
    
    
def __append_group(blend_path, name):
    """ appends the group with the given name from the given path """    
    with bpy.data.libraries.load(blend_path) as (data_from, data_to):
        if name in data_from.node_groups:
            data_to.node_groups = [name]