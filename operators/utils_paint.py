import bpy

import os
from shutil import copyfile

from .. import constants


def create_image(name, resolution, color, is_data=False):
    """ creates an image with the given parameters """
    img = bpy.data.images.new(name=name,
                            width=resolution,
                            height=resolution,
                            alpha=len(color)==4,
                            is_data=is_data)
    pixels = list(color) * (resolution * resolution)
    img.pixels = pixels
    return img


def paint_image(img):
    """ sets up the 3D view for painting on the given image """
    bpy.ops.object.mode_set(mode='TEXTURE_PAINT')
    bpy.context.scene.tool_settings.image_paint.mode = 'IMAGE'
    bpy.context.scene.tool_settings.image_paint.canvas = img
    
    
def save_all_unsaved():
    """ goes through all images and checks if they are in the lp tex folder to save """
    for img in bpy.data.images:
        if constants.TEX_DIR_NAME in img.filepath and os.path.exists(img.filepath):
            img.save()
        

def save_image(img):
    """ saves the given image if it's not saved already """
    tex_path = os.path.join(os.path.dirname(bpy.data.filepath), constants.TEX_DIR_NAME)
    img_path = os.path.join(tex_path, img.name)

    if img.is_dirty or not os.path.exists(img_path):

        if bpy.data.is_saved:

            if not os.path.exists(tex_path):
                os.makedirs(tex_path)

            if not constants.TEX_DIR_NAME in img.filepath:
                copyfile(img.filepath, img_path)
                img.filepath = img_path
                img.reload()
                
            img.save()