import bpy


def remove_connected_left(ntree, node):
    """ removes this node and all that are connected to its inputs recursively """
    for inp in node.inputs:
        for link in inp.links:
            remove_connected_left(ntree, link.from_node)
    ntree.nodes.remove(node)