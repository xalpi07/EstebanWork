name= input("Ingrese su nombre: ")
lastname = input("Ingrese su apellido: ")
age = int(input("Ingrese su edad: "))
if age < 1:
    print("Bebé")           
elif age < 13:
    print("Niño")       
elif age < 18:
    print("Preadolescente")
elif age < 21:
    print("Adolescente")    
elif age < 26:
    print("Adulto joven")
elif age < 60:
    print("Adulto") 
else:
    print("Adulto mayor") 