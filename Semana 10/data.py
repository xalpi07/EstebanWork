import csv
import os

def import_from_csv(): 
    students = []
    current_dir = os.path.dirname(__file__)  
    file_path = os.path.join(current_dir, 'students.csv')
    
    try:
        with open(file_path, mode='r',encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                row['español'] = float(row['español'])
                row['inglés'] = float(row['inglés'])
                row['sociales'] = float(row['sociales'])
                row['ciencias'] = float(row['ciencias'])
                students.append(row)
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
            writer.writerow(student)
    print("Datos exportados a 'students.csv' con éxito.")
    print("-" * 50) 
    print("\n" * 1)