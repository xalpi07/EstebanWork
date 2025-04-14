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
        self.left_arm = Arm(Hand())
        self.right_arm = Arm(Hand())
        self.left_leg = Leg(Feet())
        self.right_leg = Leg(Feet())
        self.torso = Torso(self.head, self.left_arm, self.right_arm, self.left_leg, self.right_leg)


human = Human()

print(f"The head has {human.head.eyes} eyes.")
print(f"The head has {human.head.ears} ears.")
print(f"The head has {human.head.nose} nose.")
print(f"The head has {human.head.mouth} mouth.")
print(f"The right hand has {human.right_arm.hand.fingers} fingers.")
print(f"The left hand has {human.left_arm.hand.fingers} fingers.")
print(f"The left foot has {human.left_leg.feet.toes} toes.")
print(f"The right foot has {human.right_leg.feet.toes} toes.")