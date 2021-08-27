import bpy
from bpy_extras.io_utils import ImportHelper
import bpy.utils.previews

import os
import json
from shutil import copyfile

from .. import utils, constants

    
class LP_AssetImportProps(bpy.types.PropertyGroup):
    
    name: bpy.props.StringProperty()
    
    use_group: bpy.props.BoolProperty(name="Import",
                                    description="Use group for import",
                                    default=True)
    
    asset_type: bpy.props.EnumProperty(name="Type",
                                    description="Type of this asset in LP",
                                    items=[("MASK","Mask","Layer Painter Mask"),
                                           ("FILTER","Filter","Layer Painter Filter")])
    

class LP_OT_LoadFile(bpy.types.Operator, ImportHelper):
    bl_idname = "lp.load_file"
    bl_label = "Add Asset File"
    bl_description = "Loads an asset file into layer painter"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    filename_ext = '.blend'
    
    filter_glob: bpy.props.StringProperty(
        default='*.blend',
        options={'HIDDEN'}
    )

    def execute(self, context):
        # call processing popup
        if ".blend" in self.filepath:
            bpy.ops.lp.process_file("INVOKE_DEFAULT", filepath=self.filepath)
        return {"FINISHED"}


class LP_OT_ProcessFile(bpy.types.Operator):
    bl_idname = "lp.process_file"
    bl_label = "Process Asset File"
    bl_description = "Allows you to select what groups to use for the asset file"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    filepath: bpy.props.StringProperty(options={"HIDDEN"})
    
    groups: bpy.props.CollectionProperty(type=LP_AssetImportProps)
    
    def draw(self, context):
        layout = self.layout
        
        if len(self.groups) == 0:
            layout.label(text="No node groups found!")
        
        # draw groups
        col = layout.column(align=True)
        for group in self.groups:
            box = col.box()
            subcol = box.column(align=True)
            row = subcol.row()
            row.prop(group, "use_group", text="")

            subrow = row.row()
            subrow.enabled = group.use_group
            subrow.label(text=group.name)
            subrow.prop(group, "asset_type", text="")

    def invoke(self, context, event):
        # load all group names from selected file
        self.groups.clear()
        with bpy.data.libraries.load(self.filepath, link=False) as (data_from, data_to):
            for name in data_from.node_groups:
                item = self.groups.add()
                item.name = name
        return context.window_manager.invoke_props_dialog(self, width=350)

    def build_file_data(self):
        # build data from groups
        file_data = {"file_name": os.path.split(self.filepath)[1], "uid": utils.make_uid(), "masks": [], "filters": []}
        
        for group in self.groups:
            if group.use_group:
                
                if group.asset_type == "MASK":
                    file_data["masks"].append( {"name": group.name, "thumbnail": ""} )
                elif group.asset_type == "FILTER":
                    file_data["filters"].append( {"name": group.name, "thumbnail": ""} )
                    
        return file_data
    
    def add_file_to_assets(self, file_name, uid):
        # copy file to asset files folder with uid as filename
        copyfile(self.filepath, os.path.join(constants.ASSET_LOC, f"{uid}.blend"))
    
    def add_data_to_json(self, file_data):
        # write the file data to the asset json file
        with open(constants.ASSET_FILE, "r+") as asset_file:
            data = json.loads(asset_file.read())
            data["files"].append(file_data)
            asset_file.seek(0)
            asset_file.write(json.dumps(data, indent=4))
            asset_file.truncate()

    def execute(self, context):
        # build file data
        file_data = self.build_file_data()
        
        # write file and data to asset locations
        if len(file_data["masks"]) + len(file_data["filters"]) > 0:
            self.add_file_to_assets(file_data["file_name"], file_data["uid"])
            self.add_data_to_json(file_data)
            
        load_assets(context)
        utils.redraw()
        return {"FINISHED"}


preview_collections = {}


def get_pcoll(coll_type):
    """ returns the preview collection with the given name """
    return preview_collections[coll_type]


def remove_pcolls():
    """ removes all preview collections """
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
    
    
def __assign_asset_data(item, element, asset_type, blend_file):
    """ assigns the given asset info to the given item """
    item.name = element["name"]
    item.thumbnail = element["thumbnail"]
    item.asset_type = asset_type
    item.blend_file = blend_file
    
    
def load_assets(context):
    """ loads all available assets from the asset file into the property groups """
    context.scene.lp.mask_assets.clear()
    context.scene.lp.filter_assets.clear()
    remove_pcolls()

    mask_pcoll = bpy.utils.previews.new()
    mask_pcoll.load("NONE", os.path.join(constants.ICON_LOC, "no_ico.jpg"), 'IMAGE')
    filter_pcoll = bpy.utils.previews.new()
    filter_pcoll.load("NONE", os.path.join(constants.ICON_LOC, "no_ico.jpg"), 'IMAGE')

    with open(constants.ASSET_FILE, "r") as asset_data:
        data = json.loads(asset_data.read())
        for asset_file in data["files"]:

            for element in asset_file["masks"]:
                mask = context.scene.lp.mask_assets.add()
                __assign_asset_data(mask, element, "MASK", f"{asset_file['uid']}.blend")

                if element["thumbnail"] and os.path.exists(element["thumbnail"]):
                    mask_pcoll.load(element["name"], element["thumbnail"], 'IMAGE')
                else:
                    mask_pcoll.load(element["name"], os.path.join(constants.ICON_LOC, "no_ico.jpg"), 'IMAGE')
            
            for element in asset_file["filters"]:
                filter = context.scene.lp.filter_assets.add()
                __assign_asset_data(filter, element, "FILTER", f"{asset_file['uid']}.blend")

                if element["thumbnail"] and os.path.exists(element["thumbnail"]):
                    filter_pcoll.load(element["name"], element["thumbnail"], 'IMAGE')
                else:
                    filter_pcoll.load(element["name"], os.path.join(constants.ICON_LOC, "no_ico.jpg"), 'IMAGE')

    preview_collections[constants.PCOLL_MASK] = mask_pcoll
    preview_collections[constants.PCOLL_FILTER] = filter_pcoll
    
    
class LP_OT_ReloadAssets(bpy.types.Operator):
    bl_idname = "lp.reload_assets"
    bl_label = "Reload Assets"
    bl_description = "Reload assets"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        load_assets(context)
        return {"FINISHED"}
    
    
def find_asset_file_index(files, uid):
    """ returns the index of the given uid in the file list """
    for index, data in enumerate(files):
        if data["uid"] == uid:
            return index
    
    
class LP_OT_RemoveAssetFile(bpy.types.Operator):
    bl_idname = "lp.remove_asset_file"
    bl_label = "Remove Asset File"
    bl_description = "Removes this asset file"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    uid: bpy.props.StringProperty(options={"HIDDEN"})
    
    def delete_file(self, filename):
        os.remove(os.path.join(constants.ASSET_LOC, filename))

    def execute(self, context):
        # remove uid from assets and delete file
        with open(constants.ASSET_FILE, "r+") as asset_file:
            data = json.loads(asset_file.read())
            file_data = data["files"].pop( find_asset_file_index(data["files"], self.uid) )
            self.delete_file( file_data["uid"]+".blend" )
            asset_file.seek(0)
            asset_file.write(json.dumps(data, indent=4))
            asset_file.truncate()

        load_assets(context)
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
    
    
class LP_OT_RemoveAsset(bpy.types.Operator):
    bl_idname = "lp.remove_asset"
    bl_label = "Remove Asset"
    bl_description = "Removes this asset"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    uid: bpy.props.StringProperty(options={"HIDDEN"})
    name: bpy.props.StringProperty(options={"HIDDEN"})
    asset_type: bpy.props.StringProperty(options={"HIDDEN"})

    def execute(self, context):
        # remove name from uid file in asset list
        with open(constants.ASSET_FILE, "r+") as asset_file:
            data = json.loads(asset_file.read())

            for i, item in enumerate( data["files"][ find_asset_file_index(data["files"], self.uid) ][self.asset_type] ):
                if item["name"] == self.name:
                    data["files"][ find_asset_file_index(data["files"], self.uid) ][self.asset_type].pop(i)
                    break

            asset_file.seek(0)
            asset_file.write(json.dumps(data, indent=4))
            asset_file.truncate()
            
        load_assets(context)
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)


class LP_OT_LoadThumbnail(bpy.types.Operator, ImportHelper):
    bl_idname = "lp.load_thumbnail"
    bl_label = "Load Thumbnail"
    bl_description = "Loads the thumbnail for this asset"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    uid: bpy.props.StringProperty(options={"HIDDEN"})
    name: bpy.props.StringProperty(options={"HIDDEN"})
    asset_type: bpy.props.StringProperty(options={"HIDDEN"})
    
    def execute(self, context):
        # load thumbnail
        if self.filepath.split(".")[-1] in ["jpg","jpeg","png"]:

            with open(constants.ASSET_FILE, "r+") as asset_file:
                data = json.loads(asset_file.read())

                for i, item in enumerate( data["files"][ find_asset_file_index(data["files"], self.uid) ][self.asset_type] ):
                    if item["name"] == self.name:
                        item["thumbnail"] = bpy.path.abspath(self.filepath)
                        break

                asset_file.seek(0)
                asset_file.write(json.dumps(data, indent=4))
                asset_file.truncate()

        load_assets(context)
        return {"FINISHED"}


class LP_OT_LoadThumbnails(bpy.types.Operator, ImportHelper):
    bl_idname = "lp.load_thumbnails"
    bl_label = "Load Thumbnails"
    bl_description = "Loads the thumbnails for this asset file"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    uid: bpy.props.StringProperty(options={"HIDDEN"})
    
    def execute(self, context):
        # load thumbnails
        directory = os.path.dirname(self.filepath)
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        
        with open(constants.ASSET_FILE, "r+") as asset_file:
            data = json.loads(asset_file.read())

            for name in files:
                for item in data["files"][ find_asset_file_index(data["files"], self.uid) ]["masks"]:
                    if name.split(".")[0] == item["name"] and name.split(".")[-1] in ["jpg","jpeg","png"]:
                        item["thumbnail"] = os.path.join(directory, name)

                for item in data["files"][ find_asset_file_index(data["files"], self.uid) ]["filters"]:
                    if name.split(".")[0] == item["name"] and name.split(".")[-1] in ["jpg","jpeg","png"]:
                        item["thumbnail"] = os.path.join(directory, name)

            asset_file.seek(0)
            asset_file.write(json.dumps(data, indent=4))
            asset_file.truncate()

        load_assets(context)
        return {"FINISHED"}