import bpy

from .... import utils, constants


# holds cached materials and inputs for faster repeated access
cached_materials = {}
cached_inputs = {}


def clear_caches():
    """ clears the cached materials and inputs """
    global cached_materials
    cached_materials = {}
    global cached_inputs
    cached_inputs = {}


class LP_ChannelProperties(bpy.types.PropertyGroup):

    @property
    def __material_by_ref(self):
        """ returns the material matching the channels uid reference to it """
        for material in bpy.data.materials:
            if material.lp.uid == self.mat_uid_ref:
                cached_materials[self.mat_uid_ref] = material
                return material

    @property
    def mat(self):
        """ returns the material this channel belongs to from cache or uid reference """
        global cached_materials
        if self.mat_uid_ref in cached_materials:
            try:
                if cached_materials[self.mat_uid_ref].name:
                    return cached_materials[self.mat_uid_ref]
            except:
                return self.__material_by_ref

        return self.__material_by_ref

    @property
    def inp(self):
        """ returns the input this channels belongs to from cache or uid or returns None if it doesn't exist """
        global cached_inputs
        if self.uid in cached_inputs:
            if cached_inputs[self.uid].node:
                return cached_inputs[self.uid]

        for node in self.mat.node_tree.nodes:
            for inp in node.inputs:
                if hasattr(inp, "uid") and inp.uid == self.uid:
                    cached_inputs[self.uid] = inp
                    return inp

        return None

    @property
    def is_data(self):
        """ returns if this channel is a non color channel or not """
        if self.inp.bl_idname == constants.SOCKETS["COLOR"]:
            if self.inp.node.bl_idname in [constants.NODES["NORMAL"]]:
                return True
            return False
        return True


    # reference to the uid of the material this channel is in
    mat_uid_ref: bpy.props.StringProperty()

    # uid to reference this channel which matches the input.uid
    uid: bpy.props.StringProperty(name="UID",
                                  description="UID of this channel. Empty if it hasn't been used by LP yet",
                                  default="")

    # defines if this channel will be enabled by default when adding a new layer
    default_enable: bpy.props.BoolProperty(name="Enable",
                                           description="Turn on to enable this channel by default when adding a layer",
                                           default=False)


    def update_channel_appearance(self, context):
        """ updates this channel on all layers """
        for layer in self.mat.lp.layers:
            layer.update_channel_appearance(self)

    # display name of this channel
    name: bpy.props.StringProperty(name="Name",
                                   description="Name of this channel",
                                   default="",
                                   update=update_channel_appearance)


    def init(self, inp, mat_uid):
        """ called when this channel is created to do set up """
        self.uid = utils.make_uid()
        inp.uid = self.uid

        self.mat_uid_ref = mat_uid

        self["name"] = inp.name


    def disable(self):
        """ stops this channels input from being associated with this channel """
        if self.inp:
            self.inp.uid = ""


    # include this channel in baking or not
    bake: bpy.props.BoolProperty(name="Bake",
                                description="Bake this channel",
                                default=True)

    # used to display the status of this channel bake in the ui during exporting
    completed_bake: bpy.props.BoolProperty(default=False)