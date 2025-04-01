def sort_songs(path):
    with open(path) as file:
        songs = file.readlines()
    songs.sort()
    with open('sorted_songs.txt', 'w') as file:
        for song in songs:
            file.write(song)
sort_songs('songs.txt')