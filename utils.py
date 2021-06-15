import bpy
from uuid import uuid4


def get_unique_name( collection, basename, separator=".", name_prop="name" ):
    """ returns a unique name for the given collection made up of the basename, the separator and a number """
    number = 0
    for item in collection:
        num = getattr(item, name_prop).split(separator)[-1]
        if num.isnumeric():
            num = int(num)
            number = max(num, number)
    return basename + separator + str(number+1).zfill(3)


def redraw():
    """ redraws all areas to update the ui """
    for area in bpy.context.screen.areas:
        area.tag_redraw()


def make_uid( length=10 ):
    """ returns a uid with the given length """
    return uuid4().hex[:length]


def get_active_material(context):
    """ returns the active material or None if there isn't any """
    if context.active_object and context.active_object.type == "MESH":
        return context.active_object.active_material
    return None