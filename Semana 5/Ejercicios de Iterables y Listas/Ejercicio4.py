my_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]
new_list = []   

for index in range(0, len(my_list)):
    if my_list[index] % 2 == 0:
        new_list.append(my_list[index])

print(new_list)