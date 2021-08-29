import bpy


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


def save_unsave_images():
    """ saves all unsaved images in the file """
    for img in bpy.data.images:
        save_image(img)
        

def save_image(img):
    """ saves the current image if it's not saved already """
    #  TODO