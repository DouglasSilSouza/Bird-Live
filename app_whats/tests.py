def teste1(algo=None):
    global text
    text = f"Texto função 1 {algo}"
    return text

def teste2():
    teste1()
    text2 = text
    return text2

print(teste2())