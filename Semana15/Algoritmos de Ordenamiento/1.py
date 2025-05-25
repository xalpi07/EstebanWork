def bubble_sort(arr):
    for i in range(0, len(arr)- 1):
        for j in range(0, len(arr) - 1):
            current = arr[j]
            next = arr[j + 1]
            if current > next:
                arr[j] = next
                arr[j + 1] = current
        
array = [34, 12, 5, 66, 23, 1, 89, 45, 17, 8]
print("Original:", array)
bubble_sort(array)
print("Sorted:", array)

