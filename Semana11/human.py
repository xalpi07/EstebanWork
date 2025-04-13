class Head:
    def __init__(self):
        self.eyes = 2
        self.ears = 2
        self.nose = 1
        self.mouth = 1

class Hand:
    def __init__(self):
        self.fingers = 5

class Arm:
    def __init__(self, hand):
        self.hand = hand

class Leg:
    def __init__(self, feet):
        self.feet = feet

class Feet:
    def __init__(self):
        self.toes = 5

class Torso:
    def __init__(self, head, left_arm, right_arm, left_leg, right_leg):
        self.head = head
        self.left_arm = left_arm
        self.right_arm = right_arm
        self.left_leg = left_leg
        self.right_leg = right_leg

class Human:
    def __init__(self):
        self.head = Head()
        self.left_hand = Hand()
        self.right_hand = Hand()
        self.left_arm = Arm(self.left_hand)
        self.right_arm = Arm(self.right_hand)
        self.left_feet = Feet()
        self.right_feet = Feet()
        self.left_leg = Leg(self.left_feet)
        self.right_leg = Leg(self.right_feet)
        self.torso = Torso(self.head, self.left_arm, self.right_arm, self.left_leg, self.right_leg)

human = Human()
print(f"El humano tiene {human.head.eyes} ojos.")
print(f"La mano derecha tiene {human.right_hand.fingers} dedos.")
print(f"La mano izquierda tiene {human.left_hand.fingers} dedos.")
print(f"El pie izquierdo tiene {human.left_leg.feet.toes} dedos.")
print(f"El pie derecho tiene {human.right_leg.feet.toes} dedos.")
print(f"El humano tiene {human.head.nose} nariz.")
print(f"El humano tiene {human.head.mouth} boca.")
print(f"El humano tiene {human.head.ears} orejas.")     