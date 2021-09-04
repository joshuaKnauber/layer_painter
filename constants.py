import os


# id names of different nodes for cleaner notation
NODES = {
    "TEX":      "ShaderNodeTexImage",
    "MAPPING":  "ShaderNodeMapping",
    "COORDS":   "ShaderNodeTexCoord",
    "PRINC":    "ShaderNodeBsdfPrincipled",
    "MIX":      "ShaderNodeMixRGB",
    "RGB":      "ShaderNodeRGB",
    "OUT":      "ShaderNodeOutputMaterial",
    "NORMAL":   "ShaderNodeNormalMap",
    "BUMP":     "ShaderNodeBump",
    "DISP":     "ShaderNodeDisplacement",
    "FRAME":    "NodeFrame",
    "EMIT":     "ShaderNodeEmission",
    "RAMP":     "ShaderNodeValToRGB",
    "CURVES":   "ShaderNodeRGBCurve",
    "GROUP":    "ShaderNodeGroup",
    "GROUP_IN": "NodeGroupInput",
    "GROUP_OUT":"NodeGroupOutput",
}


# id names of different sockets for cleaner notation
SOCKETS = {
    "COLOR":        "NodeSocketColor",
    "FLOAT":        "NodeSocketFloat",
    "FLOAT_FACTOR": "NodeSocketFloatFactor",
}


# name of the opacity node inside a layer
OPAC_NAME = "OPACITY"


# name of the group input node inside a lp node group
INPUT_NAME = "INPUTS"

# name of the group output node inside a lp node group
OUTPUT_NAME = "OUTPUTS"


# name of the mix node inside a mask node group
MIX_MASK = "MASK_MIX"


# name of the preview emission node
PREVIEW_EMIT_NAME = "LP Preview Emit"

# name of the preview output node
PREVIEW_OUT_NAME = "LP Preview Out"


# name of the export emission node
EXPORT_EMIT_NAME = "LP Export Emit"

# name of the export output
EXPORT_OUT_NAME = "LP Export Out"

# name of the temporary bake image
BAKE_IMG_NAME = "TMP_BAKE"

# name of the temporary bake image node
BAKE_IMG_NODE = "TMP_TEX"


# location of the asset blend files
ASSET_LOC = os.path.join(os.path.dirname(__file__), "assets", "files")

# location of the asset json file
ASSET_FILE = os.path.join(os.path.dirname(__file__), "assets", "assets.json")

# location of the lp icons
ICON_LOC = os.path.join(os.path.dirname(__file__), "assets", "icons")

# location of the lp asset images
IMG_LOC = os.path.join(os.path.dirname(__file__), "assets", "files", "imgs")


# pcoll name for masks
PCOLL_MASK = "masks"

# pcoll name for filters
PCOLL_FILTER = "filters"


# name for a layers layer filter node group
def LAYER_FILTER_NAME(layer):
    return f".{layer.uid}_filters"


# name for the rotate shortcut item
ROTATE_KEY = "ROTATE_HDRI"