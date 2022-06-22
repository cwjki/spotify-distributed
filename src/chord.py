import sys
import random
import threading
import time
import Pyro4
from utils import hashing, get_chord_node_instance, print_node_info


@Pyro4.expose
class ChordNode:
    def __init__(self, idx, m) -> None:
        self._id = idx
        self.m = m
        self.size = pow(2, m)

    @property
    def id(self):
        return self._id

    @property
    def successor(self):
        return get_chord_node_instance(self._node_finger_table[1])

    @successor.setter
    def successor(self, new_node):
        self._node_finger_table[1] = new_node
        self._successor_list = []

    @property
    def predecessor(self):
        return get_chord_node_instance(self._node_finger_table[0])

    @predecessor.setter
    def predecessor(self, new_node):
        self._node_finger_table[0] = new_node
        self._predecessor_keys = self.predecessor.keys

    @property
    def successors_list(self):
        return self._successor_list

    @property
    def node_finger_table(self):
        return self._node_finger_table

    @property
    def finger_table(self):
        return [(self._finger_table_start[i], self._node_finger_table[i]) for i in range(1, self.m + 1)]

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

    def closest_preceding_finger(self, idx) -> 'ChordNode':
        '''
        Return the closest node in the finger table preciding idx
        '''
        for i in range(self.m, 0, -1):
            if self.in_range(self._node_finger_table[i], self.id + 1, idx):
                node_id = self._node_finger_table[i]
                return get_chord_node_instance(node_id)
        return self

    def find_predecessor(self, idx) -> 'ChordNode':
        '''
        Ask node n to find idx's predecessor
        '''
        node = self
        temp_node = self
        while not self.in_range(idx, node.id + 1, node.node_finger_table[1] + 1):
            node = node.closest_preceding_finger(idx)
            if not node or node.id == temp_node.id:
                break
            temp_node = node
        return node

    def find_successor(self, idx) -> 'ChordNode':
        '''
        Ask node n to find idx's successor
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

        self._finger_table_start = [None] * (self.m + 1)

        for i in range(1, self.m + 1):
            self._finger_table_start[i] = (self.id + pow(2, i-1)) % self.size

        self._node_finger_table = [None] * (self.m + 1)

        if node_id:
            node = get_chord_node_instance(node_id)
            try:
                self.init_finger_table(node)
                self.update_others()

                print(f'\nJoin node {self.id} with {node_id}')
            except:
                print(f'\nError: Could not join node {self.id} with {node_id}')
                return False

        # if is the first node in the ring
        else:
            self._node_finger_table = [self.id] * (self.m + 1)
            print(f'\nJoin the first node {self.id}')

        print_node_info(self)
        return True

    def init_finger_table(self, node):
        '''
        Initialize finger table of local node
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

        for i in range(1, self.m):
            if self.in_range(self._finger_table_start[i+1], self.id, self._node_finger_table[i]):
                self._node_finger_table[i+1] = self.node_finger_table[i]
            else:
                self._node_finger_table[i+1] = node.find_successor(
                    self._finger_table_start[i+1]).id

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
        for i in range(1, self.m + 1):
            predecessor = self.find_predecessor(
                (self.id - pow(2, i-1)) % self.size)
            if predecessor and predecessor.id != self.id:
                predecessor.update_finger_table(self.id, i)

    def update_finger_table(self, s, i):
        '''
        If s is the ith finger of the local node, update local node 
        finger table with s
        '''
        if self.in_range(s, self.id, self._node_finger_table[i]):
            if i == 1:
                self.successor = s
            else:
                self._node_finger_table[i] = s
            predecessor = self.predecessor
            if predecessor and predecessor.id != s:
                predecessor.update_finger_table(s, i)

    def stabilize(self):
        '''
        Periodically verify local node's inmediate successor and 
        tell the successor about local node
        '''
        if self.successor is None:
            if self._successor_list:
                self.successor = self._successor_list.pop(0)
            else:
                self.successor = self.id

        node = self.successor.predecessor
        if node and self.in_range(node.id, self.id + 1, self._node_finger_table[1]) and ((self.id + 1) % self.size) != self._node_finger_table[1]:
            self.successor = node.id
        if self.successor:
            self.successor.notify(self)

    def notify(self, node):
        '''
        Local node thinks that the node might be his predecessor
        '''
        if not self.predecessor:
            for key in self._predecessor_keys.keys():
                self._keys[key] = self._predecessor_keys[key]
                if self.successor and self.successor.id != self.id:
                    self.successor.update_predecessor_key(key, self._keys[key])

        if not self.predecessor or self.in_range(node.id, self._node_finger_table[0] + 1, self.id):
            self.predecessor = node.id

    def update_predecessor_key(self, key, value):
        '''
        Update the value of a key in predecessor_key dictionary
        '''
        self._predecessor_keys[key] = value

        # try:
        #     self._predecessor_keys[key].extend(value)
        # except:
        #     self._predecessor_keys[key] = value

    def fix_fingers(self):
        '''
        Periodically refresh finger table
        '''
        i = random.randint(2, self.m)
        node = self.find_successor(self._finger_table_start[i])
        if node:
            self._node_finger_table[i] = node.id

    def update_successor_list(self):
        while True:
            try:
                if not self._successor_list:
                    if self.successor and self.successor.id != self.id:
                        self._successor_list.append(self.successor.id)

                elif len(self._successor_list) < self.m:
                    for i in range(len(self._successor_list)):
                        succ = get_chord_node_instance(self._successor_list[i])
                        if succ:
                            new_succ = succ.successor
                            if new_succ and new_succ.id != self.id and new_succ.id not in self._successor_list:
                                self._successor_list.insert(i+1, new_succ.id)
                                break
            except:
                pass

            time.sleep(1)

    def lookup(self, key):
        '''
        Return the node responsible for storing the key
        '''
        while True:
            if self.in_range(key, self.node_finger_table[0] + 1, self.id + 1):
                return self
            else:
                for k in range(1, self.m):
                    if self.in_range(key, self._finger_table_start[k], self._finger_table_start[k + 1]):
                        node = get_chord_node_instance(
                            self.node_finger_table[k])
                        if node:
                            return node.lookup(key)
                else:
                    node = get_chord_node_instance(
                        self.node_finger_table[self.m])
                    if node:
                        return node.lookup(key)

    def save_key(self, key, value):
        '''
        Save a key and its value in the Chord Ring, 
        if operation was successfully return True
        else return False
        '''
        node = self.lookup(key)
        if node:
            success = node.store_key(key, value)
            if success:
                node.successor.update_predecessor_key(key, value)
                print(f'AQUI Key {key} was saved in node {node.id}')
                return True
        print(f'Error: Could not save key {key} in the system')
        return False

    def store_key(self, hashx, value):
        '''
        Store key and value
        '''
        key = value[0] + value[1]
        self._keys[key] = (hashx, value[0], value[1], value[2], value[3])
        # try:
        #     self._keys[key].append(value)
        # except:
        #     self.keys[key] = [value]
        return True

    def get_value(self, key):
        '''
        Return the value of a key stored in the Chord Ring
        '''
        node = self.lookup(key)
        if node and key in node.keys.keys():
            return node.keys[key]
        return None

    def get_all_data(self):
        '''
        Return all the data store in the Chord Ring
        '''
        data = []
        data.append(self.keys)

        first_node_id = self.id
        node_id = self.successor.id
        while node_id != first_node_id:
            try:
                successor = self.successor
                data.append(successor.keys)
                node_id = successor.id
            except:
                print(
                    f'Error: Trying to get the values in the chord node {self.id}')

        return data


def stabilize_function(node: ChordNode):
    while True:
        try:
            node.stabilize()
            node.fix_fingers()
            time.sleep(1)
        except:
            pass


def print_node_function(node):
    while True:
        print_node_info(node)
        time.sleep(10)


def main(address, bits, node_address=None):
    idx = hashing(bits, address)

    node = get_chord_node_instance(idx)
    # print(node)
    # if node:
    #     print(f'Error: There is another node in the system with the same id, please try another address')
    #     return

    host_ip, host_port = address.split(':')
    try:
        deamon = Pyro4.Daemon(host=host_ip, port=int(host_port))
    except:
        print('Error: There is another node in the system with that address, please try another')
        return

    node = ChordNode(idx, bits)
    ns = Pyro4.locateNS()
    uri = deamon.register(node)
    ns.register(f'CHORD{idx}', uri)

    request_thread = threading.Thread(target=deamon.requestLoop)
    request_thread.daemon = True
    request_thread.start()

    if node_address:
        print(node_address)
        node_id = hashing(bits, node_address)
        print(f'node_id{node_id}')
        join_success = node.join(node_id)
    else:
        join_success = node.join()

    if not join_success:
        print('Error: The node was not sucessfully joined to the system')
        return

    stabilize_thread = threading.Thread(target=stabilize_function, args=[node])
    stabilize_thread.start()

    print_tables_thread = threading.Thread(
        target=print_node_function, args=[node])
    print_tables_thread.start()

    print_tables_thread = threading.Thread(
        target=node.update_successor_list, args=[])
    print_tables_thread.start()


if __name__ == '__main__':
    if len(sys.argv) == 3:
        main(address=sys.argv[1], bits=int(sys.argv[2]))
    elif len(sys.argv) == 4:
        main(address=sys.argv[1], bits=int(
            sys.argv[3]), node_address=sys.argv[2])
    else:
        print('Error: Missing arguments')
