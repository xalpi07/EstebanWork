from actions import new_student, show_students, show_top3_students, show_average_grade
from data import export_to_csv, import_from_csv
def menu():
    students = []   
    while True:
        print("1. Ingresar Estudiantes")
        print("2. Mostrar Estudiantes")
        print("3. Mostrar los mejores estudiantes")
        print("4. Mostrar el promedio de todas las notas")
        print("5. Exportar a CSV")
        print("6. Importar de CSV")
        print("7. Salir")
        
        option = input("Selecciona una opción: ")
        
        if option in {"1", "2", "3", "4", "5", "6", "7"}:
            print(f"Opción seleccionada: {option}")
            if option == "1":
                students += new_student()
            elif option == "2":
                show_students(students)
            elif option == "3":
                show_top3_students(students)
            elif option == "4":
                show_average_grade(students)
            elif option == "5":
                export_to_csv(students)
            elif option == "6":
                students += import_from_csv()
            else:
                print("Opción no válida. Por favor, selecciona una opción del 1 al 7.")
            if option == "7":
                print("Saliendo del programa...")
                break
        else:
            print("Opción no válida. Por favor, selecciona una opción del 1 al 7.")