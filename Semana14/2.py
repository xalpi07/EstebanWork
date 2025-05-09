class Node:
    def __init__(self, value):
        self.value = value
        self.next = None
        self.prev = None

class Deque:
    def __init__(self):
        self.head = None 
        self.tail = None 

    def push_left(self, value):
        new_node = Node(value)
        if self.head is None:
            self.head = self.tail = new_node
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node

    def push_right(self, value):
        new_node = Node(value)
        if self.tail is None:
            self.head = self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node

    def pop_left(self):
        popped_value = self.head.value
        self.head = self.head.next
        if self.head is None:
            self.tail = None
        else:
            self.head.prev = None
        return popped_value

    def pop_right(self):
        popped_value = self.tail.value
        self.tail = self.tail.prev
        if self.tail is None:
            self.head = None
        else:
            self.tail.next = None
        return popped_value

    def print_deque(self):
        current = self.head
        print("Deque:")
        while current is not None:
            print(f"  {current.value}")
            current = current.next
        print("---")

deque = Deque()
deque.push_left(10)
deque.push_right(20)
deque.push_left(5)
deque.push_right(30)
deque.print_deque()

print(f"Popped from left: {deque.pop_left()}")
deque.print_deque()

print(f"Popped from right: {deque.pop_right()}") 
deque.print_deque()