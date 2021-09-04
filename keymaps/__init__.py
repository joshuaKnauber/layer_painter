import bpy

from .. import constants


#keymaps
keymaps = {}


def get_shortcut(key):
    """ returns the shortcut with the given key """
    return keymaps[key][1]


def register():
    """ registers the layer painter keymaps """

    # create keymap
    global keymaps
    addon_prefs = bpy.context.preferences.addons[__name__.partition('.')[0]].preferences
    
    wm = bpy.context.window_manager
    addon_keyconfig = wm.keyconfigs.addon
    kc = addon_keyconfig

    km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")

    # shortcut for compiling
    kmi = km.keymap_items.new(
        idname="lp.rotate_background",
        type="RIGHTMOUSE",
        value="PRESS",
        shift=False,
        ctrl=False,
        alt=True,
        )
    keymaps[constants.ROTATE_KEY] = (km, kmi)


def unregister():
    """ unregisters the layer painter keymaps """
    global keymaps

    for key in keymaps:
        km, kmi = keymaps[key]
        km.keymap_items.remove(kmi)

    keymaps.clear()