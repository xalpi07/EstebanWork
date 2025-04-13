import csv
import os
from actions import Student  

def import_from_csv(): 
    students = []
    current_dir = os.path.dirname(__file__)  
    file_path = os.path.join(current_dir, 'students.csv')
    
    try:
        with open(file_path, mode='r', encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                student = Student(
                    name=row['name'],
                    section=row['section'],
                    español=float(row['español']),
                    inglés=float(row['inglés']),
                    sociales=float(row['sociales']),
                    ciencias=float(row['ciencias']) 
                )
                students.append(student)
        print(f"Datos importados de '{file_path}' con éxito.")
        print("-" * 50) 
        print("\n" * 1)
    except FileNotFoundError:
        print(f"El archivo '{file_path}' no se encontró.")
        print("-" * 50) 
        print("\n" * 1)
    return students

def export_to_csv(students):
    with open('students.csv', mode='w', newline='', encoding='utf-8') as file: 
        fieldnames = ['name', 'section', 'español', 'inglés', 'sociales', 'ciencias']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        writer.writeheader()
        for student in students:
            writer.writerow({
                'name': student.name,
                'section': student.section,
                'español': student.español,
                'inglés': student.inglés,
                'sociales': student.sociales,
                'ciencias': student.ciencias
            })
    print("Datos exportados a 'students.csv' con éxito.")
    print("-" * 50) 
    print("\n" * 1)