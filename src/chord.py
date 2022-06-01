import Pyro4


class ChordNode:
    def __init__(self, idx, m) -> None:
        self.idx = idx
        self.m = m
        self.size = pow(2, m)

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
        for i in range(self.m, 0, -1):
            if self.in_range(self.ft_node[i], self.idx + 1, idx):
                node_id = self.ft_node[i]
                return get_node_instance(node_id)
        return self

    def find_predecessor(self, idx) -> 'ChordNode':
        '''
        Find the node predecessor id
        '''
        node = self
        temp_node = self
        while not self.in_range(idx, node.idx + 1, node.ft_node[1] + 1):
            node = node.closest_finger(idx)
            if node is None or node.idx == temp_node.idx:
                break
            temp_node = node
        return node
