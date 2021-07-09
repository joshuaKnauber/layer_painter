import bpy
from . import panel_node, panel_channel


classes = (
    panel_node.LP_PT_NodeChannels,
    panel_channel.LP_PT_Channels,
)
reg_classes, unreg_classes = bpy.utils.register_classes_factory(classes)


def register():
    reg_classes()


def unregister():
    unreg_classes()
