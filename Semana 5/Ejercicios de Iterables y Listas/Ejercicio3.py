my_list = [4, 3, 6, 1, 7]
my_list_length = len(my_list) 
first_element = my_list[0]
last_element = my_list[my_list_length - 1]

new_list = []
for index in range(0, len(my_list)):
    if index == 0:
        new_list.append(last_element)
        continue
    elif index == my_list_length - 1:
        new_list.append(first_element)
        continue
    new_list.append(my_list[index])

print(new_list)