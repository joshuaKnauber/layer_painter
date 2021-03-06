import bpy
from . import panel_export


classes = (
    panel_export.LP_PT_ExportPanel,
)
reg_classes, unreg_classes = bpy.utils.register_classes_factory(classes)


def register():
    reg_classes()


def unregister():
    unreg_classes()