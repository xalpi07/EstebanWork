class Animal:
    def eat(self):
        print("This animal can eat.")

class Bird:
    def fly(self):
        print("This bird can fly.")

class FlyingAnimal(Animal, Bird): 
    def do_both(self):
        print("This animal can both eat and fly.")


flying_animal = FlyingAnimal()
flying_animal.eat()
flying_animal.fly()
flying_animal.do_both()