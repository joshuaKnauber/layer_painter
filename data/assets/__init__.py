import bpy
from . import asset


classes = (
    asset.LP_AssetProperties,
)
reg_classes, unreg_classes = bpy.utils.register_classes_factory(classes)


def register():
    reg_classes()

def unregister():
    unreg_classes()
