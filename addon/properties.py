import bpy

import json

from ..data.assets.asset import LP_AssetProperties
from .. import constants, utils


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


    def __asset_items(self, name, property, offset=0):
        items = [("NONE", f"-- Select a {name} --", f"Select a {name} to add it to the stack"), (None)]
        for i, asset in enumerate(getattr(self, property)):
            items.append( (str(i + offset), asset.name, asset.name) )
        return items

    def mask_items(self, context):
        """ returns the mask assets as a list of enum items """
        masks = self.__asset_items("mask", "mask_assets")
        filters = self.__asset_items("mask filter", "filter_assets", len(masks)-1)
        return masks + [("", "", "", 0)] + filters

    def filter_items(self, context):
        """ returns the filter assets as a list of enum items """
        return self.__asset_items("filter", "filter_assets")

    def select_mask(self, context):
        """ called when a mask is selected to reset it and add the mask """
        if self.masks.isdigit():
            index = int(self.masks)
            if index < len(self.mask_assets):
                utils.active_material(context).lp.selected.add_mask( self.mask_assets[index], True )
            else:
                utils.active_material(context).lp.selected.add_mask( self.filter_assets[index - len(self.mask_assets) - 1], False )
        self["masks"] = 0

    def select_filter(self, context):
        """ called when a filter is selected to reset it and add the filter """
        if self.filters.isdigit():
            utils.active_material(context).lp.selected.add_filter( self.filter_assets[int(self.filters)] )
        self["filters"] = 0

    # an enum of the mask assets to select for adding
    masks: bpy.props.EnumProperty(name="Masks",
                                description="Select one of these masks to add it to the stack",
                                items=mask_items,
                                update=select_mask)

    # an enum of the filter assets to select for adding
    filters: bpy.props.EnumProperty(name="Filters",
                                description="Select one of these filters to add it to the stack",
                                items=filter_items,
                                update=select_filter)