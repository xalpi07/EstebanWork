import random
random_number = random.randint(1, 10)
not_guessed= True

while not_guessed:
    user_number = int(input("Adivina el número secreto: "))
    if user_number == random_number:
        print("¡Felicidades, adivinaste el número secreto!")
        not_guessed = False
    else:
        print("Número incorrecto, intenta de nuevo")