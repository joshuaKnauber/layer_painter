import bpy
from bpy.app.handlers import persistent
import atexit

from layer_painter.utils import make_uid
from layer_painter.data import channel, layer


def set_material_uids():
    # TODO by @Joshua: Need to change the material uid on duplicated materials
    #       Is a bigger issue because layers and channels store references to their material by this uid
    for mat in bpy.data.materials:
        if not mat.lp.uid:
            mat.lp.uid = make_uid()


@persistent
def on_load_handler(dummy):
    """ runs when a blender file is loaded """
    channel.clear_caches()
    layer.clear_caches()
    set_material_uids()


@persistent
def pre_save_handler(dummy):
    """ runs before a blender file is saved """
    pass


@persistent
def depsgraph_handler(dummy):
    """ runs after the depsgraph is updated """
    set_material_uids()


def on_exit_handler():
    """ runs before blender is closed """
    pass


def register():
    bpy.app.handlers.load_post.append(on_load_handler)
    bpy.app.handlers.save_pre.append(pre_save_handler)
    bpy.app.handlers.depsgraph_update_post.append(depsgraph_handler)
    atexit.register(on_exit_handler)


def unregister():
    bpy.app.handlers.depsgraph_update_post.remove(depsgraph_handler)
    bpy.app.handlers.load_post.remove(on_load_handler)
    bpy.app.handlers.save_pre.remove(pre_save_handler)
    atexit.unregister(on_exit_handler)
