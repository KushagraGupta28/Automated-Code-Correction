
def detect_cycle(node):
    hare = tortoise = node

    while True:
        if hare is None or hare.successor is None:
            return False

        tortoise = tortoise.successor
        if hare.successor is None:
            return False
        hare = hare.successor.successor

        if hare is tortoise:
            return True
