import bpy
from bpy.app.handlers import persistent
import atexit
from .utils import make_uid
from .data import channel, layer
from .assets.assets import load_assets


def set_material_uids():
    for mat in bpy.data.materials:
        if not mat.lp.uid:
            mat.lp.uid = make_uid()
    # TODO handle duplicated materials


@persistent
def on_load_handler(dummy):
    channel.clear_caches()
    layer.clear_caches()
    set_material_uids()
    load_assets()


@persistent
def pre_save_handler(dummy):
    pass


@persistent
def depsgraph_handler(dummy):
    set_material_uids()


def on_exit_handler():
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
