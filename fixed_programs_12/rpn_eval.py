
def rpn_eval(tokens):
    def op(symbol, a, b):
        return {
            '+': lambda a, b: a + b,
            '-': lambda a, b: a - b,
            '*': lambda a, b: a * b,
            '/': lambda a, b: a / b
        }[symbol](a, b)

    stack = []

    for token in tokens:
        if isinstance(token, float):
            stack.append(token)
        elif token in ('+', '-', '*', '/'):
            a = stack.pop()
            b = stack.pop()
            stack.append(
                op(token, a, b)
            )
        else:
            raise ValueError("Invalid token")

    return stack.pop()
