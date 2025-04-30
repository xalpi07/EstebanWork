from datetime import date

class User:
    def __init__(self, name, date_of_birth):
        self.name = name
        self.date_of_birth = date_of_birth

    @property
    def age(self):
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

def requires_adult(func):
    def wrapper(user, *args, **kwargs):
        if user.age < 18:
            raise ValueError(f"User {user.name} is not an adult. Age: {user.age}")
        return func(user, *args, **kwargs)
    return wrapper

@requires_adult
def access_restricted_area(user):
    return f"Access granted to {user.name}." 

user1 = User("Alice", date(2012, 6, 15))
user2 = User("Bob", date(1990, 3, 22))

try:
    print(access_restricted_area(user1))
except ValueError as e:
    print(e)
 
try:
    print(access_restricted_area(user2))
except ValueError as e:
    print(e)