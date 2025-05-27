
def kheapsort(arr, k):
    import heapq

    heap = arr[:k+1]
    heapq.heapify(heap)
 
    for x in arr[k:]:
        yield heapq.heappushpop(heap, x)
 
    while heap:
        yield heapq.heappop(heap)
 
