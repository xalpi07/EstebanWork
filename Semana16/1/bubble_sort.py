def bubble_sort(arr):
    for i in range(0, len(arr)- 1):
        for j in range(0, len(arr) - 1):
            current = arr[j]
            next = arr[j + 1]
            if current > next:
                arr[j] = next
                arr[j + 1] = current