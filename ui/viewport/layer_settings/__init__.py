import bpy
from . import panel_layer_settings


classes = (
    panel_layer_settings.LP_PT_LayerSettingsPanel,
)
reg_classes, unreg_classes = bpy.utils.register_classes_factory(classes)


def register():
    reg_classes()


def unregister():
    unreg_classes()