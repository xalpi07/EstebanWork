def sum_numbers(current_number):
    try:
        number = float(input("Enter a number to sum: "))
        return current_number + number
    except ValueError:
        print("Invalid number")
        return current_number

def subtract_numbers(current_number):
    try:
        number = float(input("Enter a number to subtract: "))
        return current_number - number
    except ValueError:
        print("Invalid number")
        return current_number

def multiply_numbers(current_number):
    try:
        number = float(input("Enter a number to multiply: "))
        return current_number * number
    except ValueError:
        print("Invalid number")
        return current_number

def divide_numbers(current_number):
    try:
        number = float(input("Enter a number to divide: "))
        if number == 0:
            print("You can't divide by zero")
            return current_number
        return current_number / number
    except ValueError:
        print("Invalid number")
        return current_number

def clear_result():
    print("Result cleared.")
    return 0

def calculator():
    current_number = 0
    while True:
        print("\n" + "-" * 30 + "\n")
        print(f"Current number: {current_number}")
        print("1. Sum")
        print("2. Subtract")
        print("3. Multiply")
        print("4. Divide")
        print("5. Clear result")
        print("6. Exit")
        option = input("Select an option: ")

        if option == "1":
            current_number = sum_numbers(current_number)
        elif option == "2":
            current_number = subtract_numbers(current_number)
        elif option == "3":
            current_number = multiply_numbers(current_number)
        elif option == "4":
            current_number = divide_numbers(current_number)
        elif option == "5":
            current_number = clear_result()
        elif option == "6":
            print("Exiting calculator...")
            break
        else:
            print("Invalid option")

if __name__ == "__main__":
    calculator()