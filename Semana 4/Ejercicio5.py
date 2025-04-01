total_grades = int(input("Ingrese la cantidad de notas: "))  # 5
grade_counter = 1
approved_grades_count = 0
failed_grades_count = 0
approved_grades_average = 0
failed_grades_average = 0
total_grades_average = 0

while grade_counter <= total_grades:
    grade = int(input(f"Ingrese la nota {grade_counter}: "))
    if grade >= 70:
        approved_grades_count += 1
        approved_grades_average += grade
    else:
        failed_grades_count += 1
        failed_grades_average += grade
    total_grades_average += grade
    grade_counter += 1

total_grades_average = total_grades_average / total_grades

if approved_grades_count == 0:
    approved_grades_average = "No hay notas aprobadas"
else:
    approved_grades_average = approved_grades_average / approved_grades_count

if failed_grades_count == 0:
    failed_grades_average = "No hay notas desaprobadas"
else:
    failed_grades_average = failed_grades_average / failed_grades_count

print(f"Cantidad de notas aprobadas: {approved_grades_count}")
print(f"Promedio de las notas aprobadas: {approved_grades_average}")
print(f"Cantidad de notas desaprobadas: {failed_grades_count}")
print(f"Promedio de las notas desaprobadas: {failed_grades_average}")
print(f"Promedio de todas las notas: {total_grades_average}")