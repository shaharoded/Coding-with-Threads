class TreeNode:
    def __init__(self, str):
        self.data = str
        self.counter = 1
        self.left = None
        self.right = None

    def get_data(self):
        return self.data

    def __eq__(self, other):
        if isinstance(other, TreeNode):
            return self.data == other.data
        return False

    def __lt__(self, other):
        if isinstance(other, TreeNode):
            return self.data < other.data
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, TreeNode):
            return self.data > other.data
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, TreeNode):
            return self.data <= other.data
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, TreeNode):
            return self.data >= other.data
        return NotImplemented

    def __repr__(self):
        return f"TreeNode({self.data!r}, counter={self.counter})"


# The tree is a binary search tree (the left/right subtree of the node contains only nodes with keys lesser/greater than the node key)
# The tree is case sensitive
# Make sure that the strings contains *only* [a-z] and [A-Z]. Do not add strings that contain other characters (including numbers and spaces)

# The Same string can be added more than once ot the tree. Keep a counter on each node to count the number of strings in that node.
# examples:
# add_str("SHERLOCK") - the counter of the node will be 1. calling another add_str("SHERLOCK")  - the counter of the node will be 2. 
# del_str("SHERLOCK") - the counter of the node will be 1 again. 
# only when the last string is deleted from a node (counter=0), the node is deleted.


import sys
import networkx as nx
import matplotlib.pyplot as plt
from threading import Lock
import threading
import random




class ShareableTree:
    data = None
    root = None
    read_count = 0
    mutex = Lock()
    rw_mutex = Lock()

    def __init__(self, file_path=None):
        # Init the tree by loading the string from a text file
        # e.g., try https://www.gutenberg.org/cache/epub/834/pg834.txt
        # read the file string by string and add it to the tree. a string contains only [a-z][A-Z].
        # e.g.,
        #  I am afraid, Watson, that I shall have to go,” said Holmes,
        #  The words: I am afraid Watson that I shall have to go said Holmes
        if file_path is None:
            self.root = None
        else:
            self.data = file_path
            # Open file and split to lines
            with open(file_path, 'r') as file:
                text = file.read()
            Words = sorted(text.split())  # Split the text with white space as delimiter, store in array
            Nodes = []
            for word in Words:
                node = TreeNode(word)
                if node not in Nodes:
                    Nodes.append(node)
                else:
                    Nodes[Nodes.index(node)].counter += 1
            # Next, create a tree out of our nodes
            self.root = self.__sorted_list_to_bst(Nodes)

    def __sorted_list_to_bst(self, lst):
        if not lst:
            return None

        mid = len(lst) // 2
        root = lst[mid]
        root.left = self.__sorted_list_to_bst(lst[:mid])
        root.right = self.__sorted_list_to_bst(lst[mid + 1:])
        return root

    def add_str(self, str_to_add):  # Writer
        # add the str to the tree. 
        # update the counter accordingly is the string exists (reduce the counter by 1). For the first string counter=1
        # return True
        def insert(root, key):
            if root is None:
                return TreeNode(key)
            else:
                if root.data == key:
                    root.counter += 1
                    return root
                elif root.data < key:
                    root.right = insert(root.right, key)
                else:
                    root.left = insert(root.left, key)
            return root
        self.rw_mutex.acquire()  # -> LOCK
        node = self.__search_node(self.root, str_to_add)
        if node is not None:
            node.counter += 1
        else:
            insert(self.root, str_to_add)
        self.rw_mutex.release()  # -> UNLOCK
        return True

    def del_str(self, str_to_del):  # Writer
        # delete str from tree
        # update the counter accordingly if the string exists (reduce the counter by 1). If counter=0, remove the node.
        # return True if the str found
        # return False if str was not found
        def delete_Node(root, key):
            # if root doesn't exist, just return it
            if not root:
                return root
            # Find the node in the left subtree	if key value is less than root value
            if root.data > key:
                root.left = delete_Node(root.left, key)
            # Find the node in right subtree if key value is greater than root value,
            elif root.data < key:
                root.right = delete_Node(root.right, key)
            # Delete the node if root.value == key
            else:
                # If there is no right children delete the node and new root would be root.left
                if not root.right:
                    return root.left
                # If there is no left children delete the node and new root would be root.right
                if not root.left:
                    return root.right
                # If both left and right children exist in the node replace its value with
                # the minmimum value in the right subtree. Now delete that minimum node
                # in the right subtree
                temp_val = root.right
                while temp_val.left:
                    temp_val = temp_val.left
                # Delete the minimum node in right subtree
                root.right = delete_Node(root.right, root.data)
            return root

        self.rw_mutex.acquire()  # -> LOCK
        node = self.__search_node(self.root, str_to_del)
        if node is not None and node.counter > 1:
            node.counter -= 1
        else:
            delete_Node(self.root, str_to_del)
        self.rw_mutex.release()  # -> UNLOCK
        return True

    def __search_node(self, root, target):
        if root is None or root.data == target:
            return root
        if target < root.data:
            return self.__search_node(root.left, target)
        return self.__search_node(root.right, target)

    def search_str(self, str_to_search):  # Reader
        # return the str if exists
        # return None if not
        self.mutex.acquire()  # -> LOCK
        self.read_count += 1
        if self.read_count == 1:
            self.rw_mutex.acquire()  # -> LOCK
        self.mutex.release()  # -> UNLOCK

        node = self.__search_node(self.root, str_to_search)
        res = node.data if node is not None else None

        self.mutex.acquire()  # -> LOCK
        self.read_count -= 1
        if self.read_count == 0:
            self.rw_mutex.release()
        self.mutex.release()  # -> UNLOCK
        return res

    def balance_tree(self):  # Writer
        # Balance the tree (https://www.programiz.com/dsa/balanced-binary-tree)
        # After balancing, the maximum height difference will be 1
        # return None
        self.rw_mutex.acquire()  # -> LOCK
        Nodes = self.__inorder_scan(self.root)  # Export tree to list
        self.root = self.__sorted_list_to_bst(Nodes)  # Re-build tree
        self.rw_mutex.release()  # -> UNLOCK
        return None

    def get_height(self):  # Reader
        # return tree height (empty tree: return -1,  only root node: return 0, etc)
        # Since the tree is balanced, all the way left should work
        def height(root):
            # Check if the binary tree is empty
            if root is None:
                # If TRUE return 0
                return 0
                # Recursively call height of each node
            leftAns = height(root.left)
            rightAns = height(root.right)

            # Return max(leftHeight, rightHeight) at each iteration
            return max(leftAns, rightAns) + 1

        self.mutex.acquire()  # -> LOCK
        self.read_count += 1
        if self.read_count == 1:
            self.rw_mutex.acquire()  # -> LOCK
        self.mutex.release()  # -> UNLOCK

        res = height(self.root)

        self.mutex.acquire()  # -> LOCK
        self.read_count -= 1
        if self.read_count == 0:
            self.rw_mutex.release()
        self.mutex.release()  # -> UNLOCK
        return res

    def __inorder_scan(self, root, nodes=[]):
        if not root:
            return
        self.__inorder_scan(root.left, nodes)
        nodes.append(root)
        self.__inorder_scan(root.right, nodes)
        return nodes

    def print_tree(self):  # Reader
        # print to console the tree from smallest to largest value, delimited by ',': e.g: 
        # >abc,bcd,def,HOLMES,SHERLOCK
        # return None
        self.mutex.acquire()  # -> LOCK
        self.read_count += 1
        if self.read_count == 1:
            self.rw_mutex.acquire()  # -> LOCK
        self.mutex.release()  # -> UNLOCK

        items = self.__inorder_scan(self.root, [])
        items = [node.data for node in items]

        self.mutex.acquire()  # -> LOCK
        self.read_count -= 1
        if self.read_count == 0:
            self.rw_mutex.release()
        self.mutex.release()  # -> UNLOCK

        print(f'>{",".join(items)}')

    def show(self):  # Reader
        # draw the tree using GUI 
        # return None
        # Create a new graph
        G = nx.Graph()

        # Add nodes and edges recursively
        def add_edges(node):
            if node is not None:
                # Add the node to the graph
                G.add_node(node.data, counter=node.counter)
                # Add edges to the left and right children
                if node.left is not None:
                    G.add_edge(node.data, node.left.data)
                    add_edges(node.left)
                if node.right is not None:
                    G.add_edge(node.data, node.right.data)
                    add_edges(node.right)

        self.mutex.acquire()  # -> LOCK
        self.read_count += 1
        if self.read_count == 1:
            self.rw_mutex.acquire()  # -> LOCK
        self.mutex.release()  # -> UNLOCK

        add_edges(self.root)
        # Draw the graph
        pos = nx.spring_layout(G)
        nx.draw_networkx(G, pos, with_labels=True, node_color='skyblue', edge_color='gray', node_size=2000, alpha=0.9)
        node_labels = nx.get_node_attributes(G, 'counter')
        nx.draw_networkx_labels(G, pos,
                                labels={node: f"\n\nCounter: {counter}" for node, counter in node_labels.items()},
                                font_size=7)

        self.mutex.acquire()  # -> LOCK
        self.read_count -= 1
        if self.read_count == 0:
            self.rw_mutex.release()
        self.mutex.release()  # -> UNLOCK

        # Save the figure to a file
        plt.savefig('ShareableTree.png')
        # Show the figure
        plt.show()
        return None


# Data structure tests
# create BST
file_path = "C:\\Users\\shaha\\PycharmProjects\\mamah_assignment5\\Rick.txt"
tree = ShareableTree(file_path)
tree.print_tree()
print(tree.get_height())
print(tree.search_str("Rick"))
print(tree.add_str("Morty"))
print(tree.search_str("Morty"))
tree.balance_tree()
tree.print_tree()
tree.del_str("Morty")
tree.print_tree()
tree.add_str("Rick")
tree.add_str("Rick")
tree.add_str("Rick")
tree.add_str("Morty")
tree.show()

if __name__ == '__main__':
    st = ShareableTree(file_path=r"file.txt")
    st.add("Arthur")
    st.remove("Conan")
    st.search("Doyle")
    st.show()



# Tests

# create a binary search tree
file_path = "C:\\Users\\shaha\\PycharmProjects\\mamah_assignment5\\Rick.txt"
tree = ShareableTree(file_path)


def test_search_bst1():
    print("Searching for value Whobba in the tree")
    result = tree.search_str("Whobba")
    print(f"Value found in the tree: {result}")


def test_search_bst2():
    print("Searching for value Pickle in the tree")
    result = tree.search_str("Pickle")
    print(f"Value found in the tree: {result}")


def test_add_bst():
    print("Adding value Pickle to the tree")
    tree.add_str("Pickle")
    print("Added value Pickle to the tree")


def test_delete_bst1():
    print("Deleting value Pickle from the tree")
    tree.del_str("Pickle")
    print("Deleted value Pickle from the tree")


def test_delete_bst2():
    print("Deleting value Rick from the tree")
    tree.del_str("Rick")
    print("Deleted value Rick from the tree")


def test_print_bst():
    print("Printing the tree")
    tree.print_tree()


def test_balance_bst():
    print("Balancing the tree")
    tree.balance_tree()
    print("Balanced the tree")


def test_get_height():
    print("Getting the height of the tree")
    height = tree.get_height()
    print(f"The height of the tree is {height}")


def test_show():
    print("Showing the tree")
    tree.show()
    print("Showed the tree")


# create a list of reader and writer functions
reader_functions = [test_search_bst1, test_search_bst2, test_print_bst, test_get_height]
writer_functions = [test_add_bst, test_delete_bst1, test_delete_bst2, test_balance_bst, test_show]

# create a number of reader and writer threads
num_readers = 37
num_writers = 11

reader_threads = []
for i in range(num_readers):
    reader_threads.append(threading.Thread(target=reader_functions[i % len(reader_functions)]))

writer_threads = []
for i in range(num_writers):
    writer_threads.append(threading.Thread(target=writer_functions[i % len(writer_functions)]))

all_threads = reader_threads + writer_threads
random.shuffle(all_threads)


# start the threads
for thread in reader_threads + writer_threads:
    thread.start()

# wait for the threads to finish
for thread in reader_threads + writer_threads:
    thread.join()

