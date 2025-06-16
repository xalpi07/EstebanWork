def sort_string(string):
    lst = string.split("-") 
    lst.sort()
    return "-".join(lst)

sorted_string = sort_string("python-variable-funcion-computadora-monitor")
print(sorted_string)
