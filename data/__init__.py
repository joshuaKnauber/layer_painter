import bpy
from . import materials, assets, export


classes = (
)
reg_classes, unreg_classes = bpy.utils.register_classes_factory(classes)


def register():
    export.register()
    assets.register()
    materials.register()
    reg_classes()

def unregister():
    unreg_classes()
    export.register()
    materials.unregister()
    assets.unregister()