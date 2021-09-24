import bpy
from bpy_extras.io_utils import ImportHelper
import os

from . import utils_paint
from ..operators import utils_operator


class LP_OT_OpenImage(bpy.types.Operator, ImportHelper):
    bl_idname = "lp.open_image"
    bl_label = "Open Image"
    bl_description = "Opens an image for this input"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    filter_glob: bpy.props.StringProperty(
        default='*.png;*.jpg;*.jpeg;*.tif;*.exr',
        options={'HIDDEN'}
    )
    
    node: bpy.props.StringProperty(options={"HIDDEN", "SKIP_SAVE"})
    node_tree: bpy.props.StringProperty(options={"HIDDEN", "SKIP_SAVE"})

    non_color: bpy.props.BoolProperty(default=False, options={"HIDDEN", "SKIP_SAVE"})

    @classmethod
    def poll(cls, context):
        return utils_operator.base_poll(context)

    def import_image(self, filepath):
        """ opens the image from the given path and saves it in the folder next to the blend file """
        img = bpy.data.images.load(filepath)
        utils_paint.save_image(img)
        return img

    def execute(self, context):
        node = bpy.data.node_groups[self.node_tree].nodes[self.node]
        
        if self.filepath and os.path.exists(self.filepath) and "." in self.filepath:
            img = self.import_image(self.filepath)
            node.image = img
            
            if self.non_color:
                img.colorspace_settings.name = "Non-Color"
            else:
                img.colorspace_settings.name = "sRGB"
        return {"FINISHED"}