import bpy
from bpy_extras.io_utils import ImportHelper
import os
from shutil import copyfile
import json
from . import operator_utils
from .. import utils
from .. import constants
from ..assets.assets import load_assets


class LP_OT_AddAssetFile(bpy.types.Operator, ImportHelper):
    bl_idname = "lp.add_asset_file"
    bl_label = "Add Asset File"
    bl_description = "Adds the given asset file to the correct folder"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    files: bpy.props.CollectionProperty(
        name='File paths', type=bpy.types.OperatorFileListElement)

    filter_glob: bpy.props.StringProperty(
        default='*.blend', options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return True

    def load_group_as_mask(self, blend_name, new_blend_name, group, data):
        """ loads the given group as a mask into the data """
        if not new_blend_name in data["masks"]:
            data["masks"][new_blend_name] = {"name": blend_name, "groups": []}

        if not group.name in data["masks"][new_blend_name]["groups"]:
            data["masks"][new_blend_name]["groups"].append(group.name)
            return True

        return False

    def log_group(self, blend_name, new_blend_name, group):
        """ writes the given node group to the corresponding json file """
        success = False

        with open(constants.ASSETS_JSON, "r+") as assets:
            data = json.loads(assets.read())

            if group.lp_group.is_mask:
                success = self.load_group_as_mask(
                    blend_name, new_blend_name, group, data)

            assets.seek(0)
            assets.truncate()
            assets.write(json.dumps(data, indent=4))

        return success

    def load_asset_file(self, path, name):
        """ loads all node groups in the blend file with the given path """
        old_groups = list(bpy.data.node_groups)
        new_blend_name = f"{utils.make_uid()}.blend"

        with bpy.data.libraries.load(path) as (data_from, data_to):
            data_to.node_groups = data_from.node_groups

        loaded = 0
        for group in bpy.data.node_groups:
            if not group in old_groups:
                loaded += int(self.log_group(name.split(".")
                              [0], new_blend_name, group))
                bpy.data.node_groups.remove(group)

        if loaded > 0:
            copyfile(path, os.path.join(constants.MASK_PATH, new_blend_name))
            self.report(
                {"INFO"}, message=f"Loaded {loaded} asset{'s' if loaded > 1 else ''}")
        else:
            self.report(
                {"WARNING"}, message="Couldn't find any assets to load!")

    def execute(self, context):
        for file in self.files:
            name = file.name
            path = os.path.join(os.path.dirname(self.filepath), name)
            self.load_asset_file(path, name)

        load_assets()
        return {"FINISHED"}
