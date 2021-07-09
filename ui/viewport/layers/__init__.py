import bpy
from . import panel_layers, ui_list_layers


classes = (
    panel_layers.LP_PT_LayerPanel,
    ui_list_layers.LP_UL_Layers,
)
reg_classes, unreg_classes = bpy.utils.register_classes_factory(classes)


def register():
    reg_classes()


def unregister():
    unreg_classes()