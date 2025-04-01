def reverse_string(string):   
    reversed_string = ""
    for letter in string:
        reversed_string = letter + reversed_string
    return reversed_string 

new_string = reverse_string("Hola mundo")  
print(new_string) 