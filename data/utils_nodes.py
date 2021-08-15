import bpy


def remove_connected_left(ntree, node):
    """ removes this node and all that are connected to its inputs recursively """
    for inp in node.inputs:
        for link in inp.links:
            remove_connected_left(ntree, link.from_node)
    ntree.nodes.remove(node)
    
    
def __get_node_list(node):
    """ returns the nodes connected """
    nodes = []
    added_names = []
    
    for inp in node.inputs:
        if inp.is_linked:
            for i, column in enumerate(__get_node_list(inp.links[0].from_node)):
                if not len(nodes) > i:
                    nodes.insert(0, [])
                for found_node in column:
                    if not found_node.name in added_names:
                        nodes[i].append(found_node)
                        added_names.append(found_node.name)

    return [[node]] + nodes


def __get_node_offsets(node, node_offset):
    node_offsets = {node.name: node_offset}
    
    for inp in node.inputs:
        if inp.is_linked:
            next = inp.links[0].from_node
            next_offsets = __get_node_offsets(next, node_offset+1)
            
            for name in next_offsets:
                if not name in node_offsets:
                    node_offsets[name] = next_offsets[name]
                node_offsets[name] = max(node_offsets[name], next_offsets[name])
    
    return node_offsets


def __get_node_list(ntree, start_node):
    node_offsets = __get_node_offsets(start_node, 0)
    
    nodes = []
    for name in node_offsets:
        if not name == start_node.name:
            while node_offsets[name] >= len(nodes):
                nodes.append([])
            nodes[node_offsets[name]].append(ntree.nodes[name])
            
    return nodes

    
spacing = 100
def organize_tree(ntree, start_node):
    """ organizes the node tree from the start node from right to left """
    # build list of nodes on each horizontal layer
    nodes = __get_node_list(ntree, start_node)
    nodes = [column for column in nodes if nodes]
    # nodes.reverse()
    
    # position nodes horizontally
    x_offset = start_node.location[0] - start_node.width - spacing
    for column in nodes[1:]:
        max_width = 0
        for node in column:
            node.location = (x_offset, 0)
            max_width = max(max_width, node.width)
        x_offset = x_offset - max_width - spacing
        
    # order nodes vertically
    
    
    # position nodes vertically
    for column in nodes:
        y_offset = start_node.location[1]
        for node in column:
            node.location = (node.location[0], y_offset)
            y_offset = y_offset - node.height - spacing