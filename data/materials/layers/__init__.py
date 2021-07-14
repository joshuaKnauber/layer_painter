import bpy
from . import layer


classes = (
    layer.LP_LayerProperties,
)
reg_classes, unreg_classes = bpy.utils.register_classes_factory(classes)


def register():
    reg_classes()

def unregister():
    unreg_classes()