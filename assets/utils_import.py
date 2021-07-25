import bpy
import os


def get_group(blend_path, name):
    """ imports the group with the given name from the blend file after checking if it already exists """
    if name in bpy.data.node_groups:
        return bpy.data.node_groups[name]
    else:
        __append_group(blend_path, name)
        return bpy.data.node_groups[name]
    
    
def __append_group(blend_path, name):
    """ appends the group with the given name from the given path """
    # NOTE Could be replaced with libraries if causing errors
    bpy.ops.wm.append(
        filepath=os.path.join(blend_path, "NodeTree", name),
        directory=os.path.join(blend_path, "NodeTree"),
        filename=name)