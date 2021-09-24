import bpy
from bpy_extras.io_utils import ImportHelper
import os

from . import utils_paint
from .. import utils, constants
from ..operators import utils_operator
from ..data.materials.layers.layer_types import layer_fill


def import_image(filepath):
    """ opens the image from the given path and saves it in the folder next to the blend file """
    img = bpy.data.images.load(filepath)
    utils_paint.save_image(img)
    return img


def load_filepath_in_node(node, filepath, non_color):
    """ loads the given filepath in the given node """
    if filepath and os.path.exists(filepath) and "." in filepath:    
        img = import_image(filepath)
        node.image = img
        
        if non_color:
            img.colorspace_settings.name = "Non-Color"
        else:
            img.colorspace_settings.name = "sRGB"


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

    def execute(self, context):
        node = bpy.data.node_groups[self.node_tree].nodes[self.node]
        load_filepath_in_node(node, self.filepath, self.non_color)
        return {"FINISHED"}


class LP_OT_OpenImages(bpy.types.Operator, ImportHelper):
    bl_idname = "lp.open_images"
    bl_label = "Open Images"
    bl_description = "Opens the selected images in their respective channels"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    filter_glob: bpy.props.StringProperty(
        default='*.png;*.jpg;*.jpeg;*.tif;*.exr',
        options={'HIDDEN'}
    )
    
    files: bpy.props.CollectionProperty(name='File paths', type=bpy.types.OperatorFileListElement)

    @classmethod
    def poll(cls, context):
        return utils_operator.base_poll(context)

    def find_channel_from_name(self, context, name):
        mat = utils.active_material(context)
        for channel in constants.CHANNEL_ABBR:
            for abbr in channel["abbr"]:
                if abbr in name:
                    for channel_name in channel["names"]:
                        for channel in mat.lp.channels:
                            if channel.name == channel_name:
                                return channel
        return None

    def execute(self, context):
        mat = utils.active_material(context)
        not_found = 0
        
        for blob in self.files:
            filepath = os.path.join(os.path.dirname(self.filepath), blob.name)
            channel = self.find_channel_from_name(context, blob.name.split(".")[0].lower())

            if not channel:
                not_found += 1
                import_image(filepath)
            else:
                layer_fill.set_channel_data_type(mat.lp.selected, channel.uid, "TEX")
                layer_fill.get_channel_mix_node(mat.lp.selected, channel.uid).mute = False
                tex_node = layer_fill.get_channel_value_node(mat.lp.selected, channel.uid)
                load_filepath_in_node(tex_node, filepath, channel.is_data)
                
        if not_found:
            self.report({"WARNING"}, message=f"{not_found} images were imported but didn't match a channel!")
        return {"FINISHED"}