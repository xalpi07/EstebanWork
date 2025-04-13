class Bus:
    def __init__(self, max_passengers):
        self.max_passengers = max_passengers
        self.passenger_list = []

    def add_passenger(self,person):
        if len(self.passenger_list) < self.max_passengers:
            self.passenger_list.append(person)
        else:
            print("Bus lleno. No se pueden agregar mas pasajeros.")

class Passenger:
    def __init__(self, name):
        self.name = name

bus = Bus(max_passengers=3)

passenger1 = Passenger("Juan")
passenger2 = Passenger("María")
passenger3 = Passenger("Carlos")
passenger4 = Passenger("Ana")

bus.add_passenger(passenger1)
bus.add_passenger(passenger2)
bus.add_passenger(passenger3)
bus.add_passenger(passenger4)

print("Lista de pasajeros en el autobús:")
for passenger in bus.passenger_list:
    print(passenger.name)