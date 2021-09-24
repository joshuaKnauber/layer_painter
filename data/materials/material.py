import bpy

from ... import utils, constants
from ...data import utils_groups
from .layers.layer import LP_LayerProperties
from .layers import layer_channels
from .channels.channel import LP_ChannelProperties


class LP_MaterialProperties(bpy.types.PropertyGroup):

    # Properties of the material

    @property
    def mat(self):
        return self.id_data

    @property
    def ntree(self):
        return self.mat.node_tree

    uid: bpy.props.StringProperty(name="UID",
                                  description="UID of this material. Empty if it hasn't been used by LP yet",
                                  default="")

    layers: bpy.props.CollectionProperty(type=LP_LayerProperties)

    def update_selected(self, context):
        """ called when a different layer is selected """
        if self.selected:
            self.update_preview()

    selected_index: bpy.props.IntProperty(name="Selected Layer",
                                    description="Index of the selected layer",
                                    min=0,
                                    default=0,
                                    update=update_selected)
    
    @property
    def selected(self):
        if self.selected_index < len(self.layers):
            layer = self.layers[self.selected_index]
            if layer.uid:
                return layer
        return None

    @property
    def layer_nodes(self):
        nodes = []
        for layer in self.layers:
            if not layer.node: raise f"Couldn't find layer node for '{layer.name}'. Delete layer to proceed."
            nodes.append(layer.node)
        return nodes
    
    channels: bpy.props.CollectionProperty(type=LP_ChannelProperties)


    ### channel dropdown
    def channel_items(self, context):
        "returns the channels of this material as a list of enum items including the layer channel"
        amount = len(self.selected.get_mask_nodes("LAYER")) if context.scene.lp.layer_nav == "MASKS" else len(self.selected.get_filter_nodes("LAYER"))
        items = [("LAYER", f"Layer ({amount} {context.scene.lp.layer_nav.title()})", "The entire layer, including all channels")]
        for channel in self.channels:
            if self.selected:
                amount = len(self.selected.get_mask_nodes(channel.uid)) if context.scene.lp.layer_nav == "MASKS" else len(self.selected.get_filter_nodes(channel.uid))
                name = f"{channel.name} ({'Not Enabled' if not self.selected.get_channel_enabled(channel.uid) else str(amount) + ' ' +  context.scene.lp.layer_nav.title()})"
                items.append( (channel.uid, name, channel.inp.name) )
        return items

    def update_selected_channel(self, context):
        """ called when the selected channel is updated """
        self.update_preview()

    @property
    def channel_name(self):
        if self.channel == "LAYER":
            return "Layer"
        else:
            return self.channel_by_uid(self.channel).name

    # this is always in relation to the selected layer. The items will only include enabled channels and LAYER
    channel: bpy.props.EnumProperty(name="Channel",
                                    description="Select the channel that should be affected",
                                    items=channel_items,
                                    update=update_selected_channel)


    ### methods to get layers
    def layer_index(self, layer):
        """ returns the index of the given layer """
        for i in range(len(self.layers)):
            if self.layers[i].uid == layer.uid:
                return i
        return -1

    def layer_uid_index(self, uid):
        """ returns the index of the given layer uid """
        for i in range(len(self.layers)):
            if self.layers[i].uid == uid:
                return i
        return -1

    def layer_by_uid(self, uid):
        """ returns the layer with the given uid """
        for layer in self.layers:
            if layer.uid == uid:
                return layer
        return None

    def layer_above(self, layer, offset=1):
        """ returns the layer which is the given amount above the given layer or None if out of range """
        index = self.layer_index(layer)
        if index+offset < len(self.layers):
            return self.layers[index+offset]
        return None

    def layer_below(self, layer, offset=1):
        """ returns the layer which is the given amount below the given layer or None if out of range """
        index = self.layer_index(layer)
        if index-offset < len(self.layers) and index-offset >= 0:
            return self.layers[index-offset]
        return None

    def layers_around(self, layer, offset=1):
        """ returns the layer above and below the given layer """
        return self.layer_below(layer, offset), self.layer_above(layer, offset)


    ### add layer
    def __add_any_layer(self, layer_type):
        """ method to add a layer of any type above the active layer in this material """
        # add layer mix group
        name = utils.get_unique_name(self.layer_nodes, "Layer", ".", "label")
        _, ngroup = utils_groups.make_group(self.ntree, name)

        # add layer and move into position
        self.layers.add()
        self.layers.move(len(self.layers)-1, self.selected_index+1)

        # count up position
        if len(self.layers) > 1:
            self.selected_index += 1

        # initialize layer
        layer = self.layers[self.selected_index]
        layer.init(ngroup, layer_type, self.uid)

        self.update_preview()

    def add_fill_layer(self):
        """ adds a fill layer above the active layer to this material """
        self.__add_any_layer("FILL")

    def add_paint_layer(self):
        """ adds a paint layer above the active layer to this material """
        self.__add_any_layer("PAINT")


    ### remove layer
    def remove_active_layer(self):
        """ removes the active layer from this material """
        below = self.layer_below(self.selected)

        # delete layer node and node group
        if self.selected.node:
            ntree = self.selected.node.node_tree
            self.mat.node_tree.nodes.remove(self.selected.node)
            bpy.data.node_groups.remove(ntree)

        # remove layer item
        self.layers.remove(self.selected_index)
        self.selected_index -= 1

        # reconnect layer below
        if below and below.node:
            layer_channels.connect_channel_outputs(below)

        self.update_preview()
        
        
    ### move layer
    def move_active_layer_up(self):
        """ moves the active layer up one spot """
        if self.selected:
            # move layer item
            self.layers.move(self.selected_index, self.selected_index+1)
            self.selected_index += 1

            # move layer
            self.selected.move_up()

            self.update_preview()

    def move_active_layer_down(self):
        """ moves the active layer down one spot """
        if self.selected:
            # move layer item
            self.layers.move(self.selected_index, self.selected_index-1)
            self.selected_index -= 1

            # move layer
            self.selected.move_down()

            self.update_preview()
            

    ### methods to get channels
    @property
    def channel_uids(self):
        """ return a list of all channel uids in the material """
        return [channel.uid for channel in self.channels]

    def channel_by_inp(self, inp):
        """ returns the channel properties matching the given input """
        for channel in self.channels:
            if hasattr(inp, "uid") and channel.uid == inp.uid:
                return channel

    def channel_by_uid(self, uid):
        """ returns the channel properties matching the given uid """
        for channel in self.channels:
            if channel.uid == uid:
                return channel

    def channel_index(self, channel):
        """ returns the index of the given channel """
        for i in range(len(self.channels)):
            if self.channels[i].uid == channel.uid:
                return i
        return -1


    def __update_layer_channels(self):
        """ updates all channel in and outputs on all layers in this material """
        for layer in self.layers:
            layer_channels.update(layer)

        self.update_preview()


    ### add channel
    def add_channel(self, inp):
        """ adds a channel for the given input """
        channel = self.channels.add()
        channel.init(inp, self.uid)

        self.__update_layer_channels()

        return channel


    ### remove channel
    def remove_channel(self, channel_uid):
        """ removes the channel for the given input """
        channel = self.channel_by_uid(channel_uid)
        index = self.channel_index(channel)

        channel.disable()
        self.channels.remove(index)

        self.__update_layer_channels()


    ### move channel
    def move_channel_up(self, channel_uid):
        """ moves the given channel up one spot """
        channel = self.channel_by_uid(channel_uid)
        index = self.channel_index(channel)

        if channel != self.channels[0]:
            self.channels.move(index, index-1)

    def move_channel_down(self, uid):
        """ moves the given channel down one spot """
        channel = self.channel_by_uid(uid)
        index = self.channel_index(channel)

        if channel != self.channels[-1]:
            self.channels.move(index, index+1)


    ### methods to deal with the channel preview
    def get_preview_channel_items(self, context):
        """ returns a list of enum items for the preview channel property """
        items = []
        for channel in self.channels:
            items.append((channel.uid, channel.name, channel.name))
        items += [(None), ("MASKS","Masks","Preview the mask stack")]
        return items

    def __remove_preview(self):
        """ checks if there's a preview node and removes it """
        # remove preview emission
        if constants.PREVIEW_EMIT_NAME in self.ntree.nodes:
            self.ntree.nodes.remove(self.ntree.nodes[constants.PREVIEW_EMIT_NAME])

        # remove preview material output
        if constants.PREVIEW_OUT_NAME in self.ntree.nodes:
            self.ntree.nodes.remove(self.ntree.nodes[constants.PREVIEW_OUT_NAME])

    def __connect_preview(self, emit):
        """ connects the top layers preview channel to the emit node """
        # connect to selected channel output
        if self.preview_channel in self.channel_uids:
            channel = self.channel_by_uid(self.preview_channel)
            inp = channel.inp

            # connect emission to channel output
            if inp:
                if len(inp.links):
                    self.ntree.links.new(inp.links[0].from_socket, emit.inputs[0])

        # connect to preview output
        elif self.selected:
            self.ntree.links.new(self.selected.node.outputs[0], emit.inputs[0])

            if self.preview_channel == "MASKS":
                self.selected.preview_masks()

    def __add_preview(self):
        """ adds a preview node for the selected channel on the top layer """
        # add material output
        out = self.ntree.nodes.new(constants.NODES["OUT"])
        out.name = constants.PREVIEW_OUT_NAME

        # set material output to active
        for node in self.ntree.nodes:
            if node.bl_idname == constants.NODES["OUT"]:
                node.is_active_output = False
        out.is_active_output = True

        # add emission and connect to output
        emit = self.ntree.nodes.new(constants.NODES["EMIT"])
        emit.inputs[0].default_value = (1, 0, 0.6, 1)
        emit.name = constants.PREVIEW_EMIT_NAME
        self.ntree.links.new(emit.outputs[0], out.inputs[0])

        self.__connect_preview(emit)

    def update_preview(self, context=None):
        """ updates the preview mode to show the selected settings """
        # disable preview if no channels
        if not len(self.channels) and self.preview_channel in self.channel_uids:
            self["use_preview"] = False
            self.__remove_preview()

        # disable preview
        else:
            self.__remove_preview()

            # enable preview
            if self.use_preview:
                self.__add_preview()

        # update viewport
        if self.selected:
            self.selected.get_layer_opacity_socket().default_value = self.selected.get_layer_opacity_socket().default_value

    use_preview: bpy.props.BoolProperty(name="Preview",
                                        description="Turn on a preview mode for this material",
                                        default=False,
                                        update=update_preview)

    preview_channel: bpy.props.EnumProperty(name="Preview",
                                            description="Select what to preview",
                                            items=get_preview_channel_items,
                                            update=update_preview)
