from random import *

def get_n() -> int:
    return randint(1, 6)

def try_one_time() -> int:
    count = 0
    rest = [1, 2, 3, 4, 5, 6,]
    while rest:
        n = get_n()
        if n in rest:
            rest.remove(n)
        count += 1
    return count

def try_more_times() -> dict:
    counts = {}
    for i in range(10000):
        count = try_one_time()
        if count in counts:
            counts[count] += 1
        else:
            counts[count] = 1
    return counts

results = try_more_times()
total = sum(results.values())
results = sorted(results.items())
for i, j in results:
    print(f"{i}: {j/total}")