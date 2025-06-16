def count_cases(string):
    upper = 0
    lower = 0
    for letter in string:
        if letter.isupper():
            upper += 1
        elif letter.islower():
            lower += 1
    return f"There’s {upper} upper cases and {lower} lower cases"   

print(count_cases("I love Sushi")) 