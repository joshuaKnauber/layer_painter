import bpy
from .. import constants
from . import preferences, properties


classes = (
    properties.LP_AddonProperties,
    preferences.LP_AddonPreferences,
)
reg_classes, unreg_classes = bpy.utils.register_classes_factory(classes)


def register():
    reg_classes()
    bpy.types.Scene.lp = bpy.props.PointerProperty(type=properties.LP_AddonProperties)


def unregister():
    del bpy.types.Scene.lp
    unreg_classes()


def prefs():
    """ returns the addon preferences """
    return bpy.context.preferences.addons[constants.MODULE].preferences
