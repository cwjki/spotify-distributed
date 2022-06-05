from typing import Dict
from typing_extensions import Self
import Pyro4
from utils import hashing, get_node_instance, print_node_info


class ChordNode:
    def __init__(self, id, m) -> None:
        self._id = id
        self.m = m
        self.size = pow(2, m)

        self._finger_table = []
        self._node_finger_table = []
        self._successor_list = []

    @property
    def id(self):
        return self._id

    @property
    def successor(self):
        return get_node_instance(self._node_finger_table[1])

    @successor.setter
    def successor(self, new_node):
        self._node_finger_table[1] = new_node
        self._succesor_list = []

    @property
    def predecessor(self):
        return get_node_instance(self._node_finger_table[0])

    @predecessor.setter
    def predecessor(self, new_node):
        self._node_finger_table[0] = new_node
        self._predecessor_keys = self.predecessor.keys

    @property
    def succesors_list(self):
        return self._succesor_list

    @property
    def node_finger_table(self):
        return self._node_finger_table

    @property
    def node_finger_table(self):
        return [(self._finger_table_start[i], self._node_finger_table[i]) for i in range(1, self.size + 1)]

    @property
    def keys(self):
        return self._keys

    @property
    def predecessor_keys(self):
        return self._predecessor_keys

    @predecessor_keys.setter
    def predecessor_keys(self, new_keys):
        self._predecessor_keys = new_keys

    def in_range(self, key, lwbound, upbound) -> bool:
        '''
        Return True if the key is between the lowerbound and the upperbound
        False in other case
        '''
        lwbound = lwbound % self.size
        upbound = upbound % self.size

        if lwbound == upbound:
            return True
        elif lwbound < upbound:
            return lwbound <= key and key < upbound
        else:
            return (lwbound <= key and key < upbound + self.size) or (lwbound <= key + self.size and key < upbound)

    def closest_finger(self, idx) -> 'ChordNode':
        '''
        Return the closest node in the finger table after node idx
        '''
        for i in range(self.size, 0, -1):
            if self.in_range(self._node_finger_table[i], self.id + 1, idx):
                node_id = self._node_finger_table[i]
                return get_node_instance(node_id)
        return self

    def find_predecessor(self, idx) -> 'ChordNode':
        '''
        Find the node predecessor id
        '''
        node = self
        temp_node = self
        while not self.in_range(idx, node.id + 1, node.node_finger_table[1] + 1):
            node = node.closest_finger(idx)
            if node is None or node.id == temp_node.id:
                break
            temp_node = node
        return node

    def find_successor(self, idx) -> 'ChordNode':
        '''
        Find the node successor id
        '''
        node = self.find_predecessor(idx)
        return node.successor if node else None

    def join(self, node_id=None) -> bool:
        '''
        If node was successfully joined return True
        else False
        '''
        self._keys = {}
        self._predecessor_keys = {}
        self._successor_list = []

        self._finger_table_start = [None] * (self.size + 1)
        self._finger_table_start = [(self.id + pow(2, i-1)) %
                                    self.size for i in range(1, self.size + 1)]

        self._node_finger_table = [None] * (self.size + 1)

        if node_id:
            node = get_node_instance(node_id)
            try:
                self.init_finger_table(node)
                self.update_others()
                print(f'\nJoin node {self.id} with {node_id}')
            except:
                print(f'\nError: Could not join node {self.id} with {node_id}')
                return False

        # if is the first node in the ring
        else:
            self._node_finger_table = [self.id] * (self.size + 1)
            print(f'\nJoin the first node {self.id}')

        print_node_info(self)
        return True

    def init_finger_table(self, node):
        '''
        Initialize the local finger table of a node
        '''
        self.successor = node.find_successor(self._finger_table_start[1]).id
        self.predecessor = self.successor.node_finger_table[0]

        successor_keys = self.successor.keys.keys()
        for key in successor_keys:
            if self.in_range(key, self.node_finger_table[0] + 1, self.id + 1):
                self.keys[key] = self.successor.pop_key(key)

        self.successor.successor.predecessor_keys = self.successor.keys
        self._predecessor_keys = self.predecessor.keys
        self.successor.predecessor = self.id

        for i in range(1, self.size):
            if self.in_range(self._finger_table_start[i+1], self.id, self._node_finger_table[i]):
                self._node_finger_table[i+1] = self.node_finger_table[i]
            else:
                self._node_finger_table[i+1] = node.find_successor(
                    self._node_finger_table[i+1]).id

    def pop_key(self, key):
        '''
        Delete a key in the local node and returns its value
        '''
        try:
            value = self._keys.pop(key)
            print(f'Key {key} was deleted in node {self.id}')
            return value
        except KeyError:
            print(f'KeyError: Could not delete key {key} in node {self.id}')
            return None

    def update_others(self):
        '''
        Update all nodes whose finger table should refer to a local node 
        '''
        for i in range(1, self.size + 1):
            predecessor = self.find_predecessor((self.id - pow(2, i-1)) % self.size)
            if predecessor and predecessor.id != self.id:
                predecessor.update_finger_table(self.id, i)
    
    def update_finger_table(self, s, i):
        '''
        If s is the ith finger of the local node, update local node 
        finger table with s
        '''
        if self.in_range(s, self.id, self._finger_table[i]):
            if i == 1:
                self.succesors = s
            else:
                self._node_finger_table[i] = s
            predecessor = self.predecessor
            if predecessor and predecessor.id != s:
                predecessor.update_finger_table(s, i)

    
