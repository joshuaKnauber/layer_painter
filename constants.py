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


# name of the preview output
PREVIEW_OUT_NAME = "PREVIEW"

# name of the preview emission node
PREVIEW_EMIT_NAME = "LP Preview Emit"

# name of the preview output node
PREVIEW_OUT_NAME = "LP Preview Out"


# location of the asset blend files
ASSET_LOC = os.path.join(os.path.dirname(__file__), "assets", "files")

# location of the asset json file
ASSET_FILE = os.path.join(os.path.dirname(__file__), "assets", "assets.json")