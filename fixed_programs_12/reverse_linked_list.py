
def reverse_linked_list(node):
    prevnode = None
    while node:
        nextnode = node.next
        node.next = prevnode
        prevnode = node
        node = nextnode
    return prevnode
