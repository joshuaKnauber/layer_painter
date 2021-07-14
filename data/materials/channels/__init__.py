import bpy
from . import channel


classes = (
    channel.LP_ChannelProperties,
)
reg_classes, unreg_classes = bpy.utils.register_classes_factory(classes)


def register():
    reg_classes()

def unregister():
    unreg_classes()