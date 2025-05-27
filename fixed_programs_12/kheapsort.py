
def kheapsort(arr, k):
    import heapq
 
    heap = arr[:k]
    heapq.heapify(heap)
    for x in arr:
        if len(heap) < k:
            yield heapq.heappushpop(heap, x)
    else:
            yield heapq.heappushpop(heap,x)
 
    while heap:
        yield heapq.heappop(heap)

