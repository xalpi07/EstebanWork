import json

def get_pokemon_input():
    name = input("Ingrese el nombre del Pokémon: ")
    types = input("Ingrese los tipos del Pokémon (separados por coma): ").split(',')
    
    print("Ingrese las estadísticas base del Pokémon:")
    base_stats = {
        "HP": int(input("HP: ")),
        "Attack": int(input("Attack: ")),
        "Defense": int(input("Defense: ")),
        "Sp. Attack": int(input("Sp. Attack: ")),
        "Sp. Defense": int(input("Sp. Defense: ")),
        "Speed": int(input("Speed: "))
    }
    
    return {
        "name": {"english": name},
        "type": [t.strip() for t in types],
        "base": base_stats
    }

def add_pokemon(pokemon, file_path='pokemons.json'):
    try:
        with open(file_path, 'r') as file:
            pokemons = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        pokemons = []
    
    pokemons.append(pokemon)
    
    with open(file_path, 'w') as file:
        json.dump(pokemons, file, indent=4)

def main():
    while True:
        pokemon = get_pokemon_input()
        add_pokemon(pokemon)
        
        another = input("¿Desea agregar otro Pokémon? (s/n): ").strip().lower()
        if another != 's':
            break
    print("Pokémon(s) guardado(s) en 'pokemons.json'")

if __name__ == "__main__":
    main()