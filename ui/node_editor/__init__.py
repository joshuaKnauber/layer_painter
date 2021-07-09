import bpy
from . import channels


classes = (
)
reg_classes, unreg_classes = bpy.utils.register_classes_factory(classes)


def register():
    reg_classes()
    channels.register()


def unregister():
    unreg_classes()
    channels.unregister()
