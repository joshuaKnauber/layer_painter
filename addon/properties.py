import bpy

import json

from ..data.assets.asset import LP_AssetProperties
from . import constants


class LP_AddonProperties(bpy.types.PropertyGroup):

    # navigation enum for the layer settings
    layer_nav: bpy.props.EnumProperty(name="Navigation",
                                      description="Choose which tab to show",
                                      items=[("LAYER", "Layer", "Layer settings"),
                                             ("MASKS", "Masks", "Mask settings"),
                                             ("FILTERS", "Filters", "Filter settings")])

    # expand toggle for the mapping settings
    expand_mapping: bpy.props.BoolProperty(name="Expand",
                                           description="Show the mapping settings of the layer",
                                           default=True)
    
    # mask asset items
    mask_assets: bpy.props.CollectionProperty(type=LP_AssetProperties)
    
    # filter asset items
    filter_assets: bpy.props.CollectionProperty(type=LP_AssetProperties)
    
    @property
    def asset_files(self):
        """ returns all asset files that are loaded into lp as saved in the assets.json file """
        # TODO (noted by Joshua) cache these or get them some other way to not always open that file
        asset_files = []
        with open(constants.ASSET_FILE, "r") as asset_data:
            asset_files = json.loads(asset_data.read())["files"]
        return asset_files
