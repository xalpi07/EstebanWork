class Student:
    def __init__(self, name, section, español, inglés, sociales, ciencias):
        self.name = name
        self.section = section
        self.español = español
        self.inglés = inglés
        self.sociales = sociales
        self.ciencias = ciencias

    def get_average(self):
        return (self.español + self.inglés + self.sociales + self.ciencias) / 4


def new_student():
    students = []  
    while True:
        name = input("Ingresa el nombre del estudiante: ")
        section = input("Ingresa la sección del estudiante: ")
        
        grades = {}
        for subject in ["español", "inglés", "sociales", "ciencias"]:
            while True:
                try:
                    grade = float(input(f"Ingresa la nota de {subject} del estudiante (0-100): "))
                    if 0 <= grade <= 100:
                        grades[subject] = grade
                        break
                    else:
                        print("La nota debe estar entre 0 y 100. Intenta de nuevo.")
                except ValueError:
                    print("Entrada no válida. Por favor, ingresa un número.")
        
        student = Student(name, section, grades["español"], grades["inglés"], grades["sociales"], grades["ciencias"])
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
        print(f"  Nombre: {student.name}")
        print(f"  Sección: {student.section}")
        print(f"  Notas:")
        print(f"    Español: {student.español}")
        print(f"    Inglés: {student.inglés}")
        print(f"    Sociales: {student.sociales}")
        print(f"    Ciencias: {student.ciencias}")
        print("-" * 50) 
    print("\n" * 1)


def show_top3_students(students):
    if not students:
        print("No hay estudiantes para mostrar.")
        return
    
    students.sort(key=lambda student: student.get_average(), reverse=True)
    
    print("\nLos 3 mejores estudiantes son:")
    for student in students[:3]:
        print(f"Nombre: {student.name} - Promedio: {student.get_average():.2f}")
    print("-" * 50)     
    print("\n" * 1)


def show_average_grade(students):
    if not students:
        print("No hay estudiantes para mostrar.")
        return

    total_average_grades = sum(student.get_average() for student in students)
    average_grade = total_average_grades / len(students)
    print(f"\nEl promedio general de los promedios individuales es: {average_grade:.2f}")
    print("-" * 50) 
    print("\n" * 1)