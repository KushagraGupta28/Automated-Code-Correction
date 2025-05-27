
import string
def to_base(num, b):
    result = ''
    alphabet = string.digits + string.ascii_uppercase
    if b < 2 or b > 36:
        return "Invalid base"
    while num > 0:
        i = num % b
        num = num // b
        result = alphabet[i] + result
    return result
