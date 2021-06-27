import bpy
from .. import constants
import os
import json


def __clear_assets():
    """ removes all asset references from the file """
    bpy.context.scene.lp.masks.clear()
    

def __load_masks():
    """ loads the LP masks into the file """
    with open( constants.ASSETS_JSON, "r" ) as data:
        assets = json.loads( data.read() )
        
        for blend_name in assets[ "masks" ]:
            for group in assets["masks"][blend_name][ "groups" ]:
                mask = bpy.context.scene.lp.masks.add()
                mask.name = group
                mask.blend_name = mask[ "name" ]
                mask.path_name = blend_name
                

def load_assets():
    """ loads all layer painter assets on file load or when called """
    __clear_assets()
    __load_masks()