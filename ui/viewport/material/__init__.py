import bpy
from . import panel_materials


classes = (
    panel_materials.LP_PT_MaterialPanel,
)
reg_classes, unreg_classes = bpy.utils.register_classes_factory(classes)


def register():
    reg_classes()


def unregister():
    unreg_classes()