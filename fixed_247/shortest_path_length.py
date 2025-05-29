from heapq import *

def shortest_path_length(length_by_edge, startnode, goalnode):
    unvisited_nodes = []  # Min-heap containing (distance, node) pairs
    heappush(unvisited_nodes, (0, startnode))
    visited_nodes = set()

    while len(unvisited_nodes) > 0:
        distance, node = heappop(unvisited_nodes)

        if node == goalnode:  # Use equality check, not 'is'
            return distance

        if node in visited_nodes:
            continue

        visited_nodes.add(node)

        for nextnode in node.successors:
            if nextnode in visited_nodes:
                continue

            old_dist = get(unvisited_nodes, nextnode)
            new_dist = min(old_dist if old_dist else float('inf'), distance + length_by_edge[node, nextnode])

            insert_or_update(unvisited_nodes, (new_dist, nextnode))

    return float('inf')


def get(node_heap, wanted_node):
    for dist, node in node_heap:
        if node == wanted_node:
            return dist
    return 0  # Return 0 if node not found


def insert_or_update(node_heap, dist_node):
    dist, node = dist_node
    for i, (existing_dist, existing_node) in enumerate(node_heap):
        if existing_node == node:
            node_heap[i] = dist_node
            heapify(node_heap)  # Restore heap property after replacement
            return

    
