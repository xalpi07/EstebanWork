class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

class BinaryTree:
    def __init__(self):
        self.root = None

    def insert(self, value):
        if self.root is None:
            self.root = Node(value)
        else:
            self._insert_recursively(self.root, value)

    def _insert_recursively(self, current, value):
        if value < current.value:
            if current.left is None:
                current.left = Node(value)
            else:
                self._insert_recursively(current.left, value)
        else:
            if current.right is None:
                current.right = Node(value)
            else:
                self._insert_recursively(current.right, value)

    def print_tree(self):
        print("Binary Tree:")
        self._print_recursively(self.root, level=0)
        print("---")

    def _print_recursively(self, node, level):
        if node is not None:
            self._print_recursively(node.right, level + 1)
            print("    " * level + f" {node.value}")
            self._print_recursively(node.left, level + 1)

tree = BinaryTree()
tree.insert(10)
tree.insert(5)
tree.insert(15)
tree.insert(3)
tree.insert(7)
tree.insert(12)
tree.insert(18)

tree.print_tree()