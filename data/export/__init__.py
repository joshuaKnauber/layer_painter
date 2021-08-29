import bpy
from . import export


classes = (
    export.LP_BakeProperties,
)
reg_classes, unreg_classes = bpy.utils.register_classes_factory(classes)


def register():
    reg_classes()

def unregister():
    unreg_classes()