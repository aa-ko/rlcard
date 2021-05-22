d = []
for i in range(1, 105):
    p = 1
    if i == 55:
        p = 7
    elif i % 11 == 0:
        p = 5
    elif i % 10 == 0:
        p = 3
    elif i % 5 == 0:
        p = 2
    d.append({"number": i, "penalty": p})

print(d)