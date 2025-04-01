import json

def read_and_print_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        print(json.dumps(data, indent=4))

read_and_print_json('example.json')

def write_json(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Example data about Elden Ring
elden_ring_data = {
    "title": "Elden Ring",
    "developer": "FromSoftware",
    "publisher": "Bandai Namco Entertainment",
    "release_date": "February 25, 2022",
    "genre": ["Action RPG", "Open World"],
    "platforms": ["PC", "PlayStation 4", "PlayStation 5", "Xbox One", "Xbox Series X/S"],
    "director": "Hidetaka Miyazaki",
    "game_mode": ["Single-player", "Online multiplayer"],
    "rating": 10
}

write_json('elden_ring.json', elden_ring_data)