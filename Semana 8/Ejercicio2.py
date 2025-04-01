import csv

def get_videogame_input():
    name = input("Ingrese el nombre del videojuego: ")
    genre = input("Ingrese el género: ")
    developer = input("Ingrese el desarrollador: ")
    rating = input("Ingrese la clasificación de edad (E, E10+, T, M, etc.): ")
    return {"name": name, "genre": genre, "developer": developer, "rating": rating}

def save_videogames_csv(file_path, data, headers):
    with open(file_path, 'w', newline='') as file:
        writer = csv.DictWriter(file, headers)
        writer.writeheader()
        writer.writerows(data)

def main():
    videogames_list = []
    while True:
        videogames_list.append(get_videogame_input())
        another = input("¿Desea agregar otro videojuego? (s/n): ").strip().lower()
        if another != 's':
            break
    
    if videogames_list:
        save_videogames_csv('videogames.csv', videogames_list, videogames_list[0].keys())
        print("Lista de videojuegos guardada en 'videogames.csv'")
    else:
        print("No se ingresaron videojuegos.")

if __name__ == "__main__":
    main()