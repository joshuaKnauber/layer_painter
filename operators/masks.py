import bpy

import os

from .. import constants, utils
from ..assets import utils_import
from ..operators import utils_operator


class LP_OT_AddMask(bpy.types.Operator):
    bl_idname = "lp.add_mask"
    bl_label = "Add Mask"
    bl_description = "Adds this mask"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    group_name: bpy.props.StringProperty(options={"HIDDEN"})
    file_name: bpy.props.StringProperty(options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        mat = utils.active_material(context)
        return utils_operator.base_poll(context) and mat.lp.selected

    def execute(self, context):
        group = utils_import.get_group(os.path.join(constants.ASSET_LOC, self.file_name), self.group_name)
        return {"FINISHED"}
