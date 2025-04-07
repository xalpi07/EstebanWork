def new_student():
    students = []  
    while True:
        student = {}
        student["name"] = input("Ingresa el nombre del estudiante: ")
        student["section"] = input("Ingresa la sección del estudiante: ")
        
        for subject in ["español", "inglés", "sociales", "ciencias"]:
            while True:
                try:
                    grade = float(input(f"Ingresa la nota de {subject} del estudiante (0-100): "))
                    if 0 <= grade <= 100:
                        student[subject] = grade
                        break
                    else:
                        print("La nota debe estar entre 0 y 100. Intenta de nuevo.")
                except ValueError:
                    print("Entrada no válida. Por favor, ingresa un número.")
        
        students.append(student)
        
        another = input("¿Deseas ingresar otro estudiante? (s/n): ").strip().lower()
        if another != "s":
            print("-" * 50) 
            print("\n" * 1)
            break
    return students    

def show_students(students):
    if not students:
        print("No hay estudiantes para mostrar.")
        return
    
    print("\nLista de Estudiantes:")
    print("-" * 50)  
    for num, student in enumerate(students, start=1):
        print(f"Estudiante #{num}")
        print(f"  Nombre: {student['name']}")
        print(f"  Sección: {student['section']}")
        print(f"  Notas:")
        print(f"    Español: {student['español']}")
        print(f"    Inglés: {student['inglés']}")
        print(f"    Sociales: {student['sociales']}")
        print(f"    Ciencias: {student['ciencias']}")
        print("-" * 50) 
    print("\n" * 1)

def show_top3_students(students):
    if not students:
        print("No hay estudiantes para mostrar.")
        return
    
    students_with_averages = []
    for student in students:
        average = (student['español'] + student['inglés'] + student['sociales'] + student['ciencias']) / 4
        students_with_averages.append((student, average))
    
    students_with_averages.sort(key=lambda x: x[1], reverse=True)
    
    print("\nLos 3 mejores estudiantes son:")
    for student, average in students_with_averages[:3]:
        print(f"Nombre: {student['name']} - Promedio: {average}")
    print("-" * 50)     
    print("\n" * 1)

def show_average_grade(students):
    if not students:
        print("No hay estudiantes para mostrar.")
        return

    total_average_grades = 0
    students_count = len(students)
    for student in students:
        promedio_estudiante = (student['español'] + student['inglés'] + student['sociales'] + student['ciencias']) / 4
        total_average_grades += promedio_estudiante

    average_grade = total_average_grades / students_count
    print(f"\nEl promedio general de los promedios individuales es: {average_grade:.2f}")
    print("-" * 50) 
    print("\n" * 1)