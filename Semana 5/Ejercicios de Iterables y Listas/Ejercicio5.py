max_number = 0
cont = 0
number_list = []
while cont < 10:
    number = int(input(f"{cont+1}. Ingrese un número: "))
    number_list.append(number)
    if number > max_number:
        max_number = number
    cont += 1

print(number_list)
print(f"El número más grande es: {max_number}")