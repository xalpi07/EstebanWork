string = "hola"
string2 = "adios"
print (f"{string} {string2}")
hola adios
---------------------------------

string = "hola"
string2 = "adios"
print (string + " " + string2)
hola adios
---------------------------------

string = "hola"
string2 = "adios"
print (string + " " + 2)
Error, no se puede concatenar un string con un int
---------------------------------

list = [1,2,3,4]
list2 = [5,6,7,8]
print (list + list2)
[1, 2, 3, 4, 5, 6, 7, 8]
---------------------------------

list = [1,2,3,4]
string = "adios"
print (list + string)
Error, no se pude concatear un string con una lista
---------------------------------

float = 3.14
int = 3
print (float + int)
6.140000000000001
---------------------------------

bool1 = True
bool2 = False
print (bool1 + bool2)
1
---------------------------------

bool1 = False
bool2 = False
print (bool1 + bool2)
0