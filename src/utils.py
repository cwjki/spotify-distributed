import Pyro4
import hashlib


def hashing(bits, string):
    try:
        hashx = hashlib.sha256(string.encode('utf-8', 'ignore')).hexdigest()
        hashx = int(hashx, 16) % pow(2, bits)
        return hashx
    except:
        return None


def get_chord_node_instance(idx):
    return get_proxy(f'CHORD{idx}')


def get_spotify_node_instance(idx):
    return get_proxy(f'SPOTIFY{idx}')


def get_proxy(idx):
    Pyro4.Proxy(f'PYRONAME:{idx}')
    with Pyro4.Proxy(f'PYRONAME:{idx}') as p:
        try:
            p._pyroBind()
            return p
        except:
            return None


def print_node_info(node):
    if node:
        print(f'\nNode {node.id}')
        print(f'Predecessor: {node.node_finger_table[0]}')
        print(f'Successor: {node.node_finger_table[1]}')
        # print(f'Successors List: {node.successors_list}')

        print('Finger table:')
        for i in node.finger_table:
            print(f'Start {i[0]}   Node {i[1]}')

        # print('Predecessor Keys')
        # print(node.predecessor_keys)

        print('Keys:')
        for key, value in node.keys.items():
            hashx, title, author, gender, _ = value
            print(f'Key:{key} -> {hashx}, {title}, {author}, {gender}')


def get_song_metadata(string: str):
    string = string[1:-1]
    string = string.split(', ')
    title = string[0][1:-1]
    author = string[1][1:-1]
    gender = string[2][1:-1]
    return title, author, gender
