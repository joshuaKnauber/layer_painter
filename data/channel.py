import bpy
from ..utils import make_uid


cached_materials = {}
cached_inputs = {}

def clear_caches():
    global cached_materials
    cached_materials = {}
    global cached_inputs
    cached_inputs = {}
    

class LP_ChannelProperties(bpy.types.PropertyGroup):
    

    @property
    def mat(self):
        global cached_materials
        if self.mat_uid_ref in cached_materials:
            return cached_materials[ self.mat_uid_ref ]
        
        for material in bpy.data.materials:
            if material.lp.uid == self.mat_uid_ref:
                cached_materials[ self.mat_uid_ref ] = material
                return material
            
            
    @property
    def inp(self):
        global cached_inputs
        if self.uid in cached_inputs:
            if cached_inputs[ self.uid ].node:
                return cached_inputs[ self.uid ]
        
        for node in self.mat.node_tree.nodes:
            for inp in node.inputs:
                if hasattr(inp, "uid") and inp.uid == self.uid:
                    cached_inputs[ self.uid ] = inp
                    return inp
        
        return None
            
            
    mat_uid_ref: bpy.props.StringProperty() # reference to the uid of the material this channel is in
            
            
    uid: bpy.props.StringProperty(name="UID",
                                    description="UID of this channel. Empty if it hasn't been used by LP yet",
                                    default="")
    
    
    default_enable: bpy.props.BoolProperty(name="Enable",
                                    description="Turn on to enable this channel by default when adding a layer",
                                    default=False)
    
    
    def update_channel_appearance(self, context):
        """ updates this channel on all layers """
        for layer in self.mat.lp.layers:
            layer.setup_channels(self)
    
    
    name: bpy.props.StringProperty(name="Name",
                                    description="Name of this channel",
                                    default="",
                                    update=update_channel_appearance)
    
    
    def init(self, inp, mat_uid):
        """ called first thing when this channel is created to set it up """
        self.uid = make_uid()
        inp.uid = self.uid
        
        self.mat_uid_ref = mat_uid
        
        self["name"] = inp.name
        
        
    def disable(self):
        """ stops this channels input from being associated with this channel """
        if self.inp:
            self.inp.uid = ""