from collections import deque as Queue

def breadth_first_search(startnode, goalnode):
    queue = Queue()
    queue.append(startnode)

    nodesseen = set()
    nodesseen.add(startnode)

    while Queue:
        node = queue.popleft()

        if node is goalnode:
            return True
        else:
            queue.extend(successor for successor in node.successors if successor not in nodesseen)
            nodesseen.update(node.successors)

    return False