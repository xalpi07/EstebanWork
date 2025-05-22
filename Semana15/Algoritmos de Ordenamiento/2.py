def bubble_sort_reverse(arr):
    for i in range(len(arr) - 1, 0, -1):
        for j in range(len(arr) - 1, 0, -1):
            current = arr[j]
            previous = arr[j - 1]
            if current < previous:
                arr[j] = previous
                arr[j - 1] = current

array = [34, 12, 5, 66, 23, 1, 89, 45, 17, 8]
print("Original:", array)
bubble_sort_reverse(array)
print("Sorted:", array)