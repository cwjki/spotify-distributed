import sys
import threading
import time
import Pyro4
from chord import ChordNode
from utils import get_chord_node_instance, hashing, get_spotify_node_instance


@Pyro4.expose
class SpotifyNode:
    def __init__(self, address, chord_address, m) -> None:
        self.address = address
        self.chord_id = hashing(m, chord_address)
        self.chord_successors_list = []
        self.m = m

        self._spotify_nodes_list = []

    @property
    def spotify_nodes_list(self):
        return self._spotify_nodes_list

    def add_spotify_node(self, address):
        if address not in self._spotify_nodes_list:
            self._spotify_nodes_list.append(address)

    def join(self, spotify_address):
        '''
        If spotify node was successfully joined return True
        else False
        '''
        self._spotify_nodes_list = [self.address]
        if spotify_address:
            node = get_spotify_node_instance(spotify_address)
            if node:
                try:
                    spotify_nodes = node.spotify_nodes_list
                    for addr in spotify_nodes:
                        if addr == self.address:
                            continue
                        self._spotify_nodes_list.append(addr)
                        node = get_spotify_node_instance(addr)
                        if node:
                            node.add_spotify_node(self.address)
                except:
                    return False
            else:
                return False
        return True

    def update_spotify_nodes_list(self):
        '''
        Periodically check if a spotify node is down and remove it 
        from the spotify_node_list.
        '''
        while True:
            spotify_nodes = self.spotify_nodes_list
            for addr in spotify_nodes:
                node = get_spotify_node_instance(addr)
                if not node:
                    self._spotify_nodes_list.remove(addr)
            time.sleep(1)

    def update_chord_successor_list(self):
        '''
        Periodically update the chord successor list
        '''
        while True:
            node = get_chord_node_instance(self.chord_id)
            if node:
                try:
                    self.chord_successors_list = node.successor_list
                except:
                    pass

            time.sleep(1)

    def print_node_info(self):
        '''
        Print all the node data
        '''
        while True:
            print(f'\nAddress: {self.address}')
            print(f'Chord node: {self.chord_id}')
            print(f'Chord node successors list: {self.chord_successors_list}')
            print(f'Spotify nodes list: {self.spotify_nodes_list}')
            time.sleep(10)

    def change_chord_node(self):
        for idx in self.chord_successors_list:
            node = get_chord_node_instance(idx)
            if node:
                self.chord_id = idx
                return node
        return None

    def get_song(self, song_key):
        song = None
        while True:
            chord_node = get_chord_node_instance(self.chord_id)
            if not chord_node:
                chord_node = self.change_chord_node()

            try:
                hashx = hashing(self.m, song_key)
                if not hashx:
                    print(
                        f'Error: Could not get the hash for the song key {song_key}')
                    return song

                song = chord_node.get_value(hashx)
                return song

            except:
                if not self.chord_successors_list:
                    print(
                        f'Error: Could not connect with chord node {self.chord_id}')
                    break
        return song

    def save_song(self, song_key, song_value):
        while True:
            chord_node = get_chord_node_instance(self.chord_id)
            if not chord_node:
                chord_node = self.change_chord_node()

            try:
                hashx = hashing(self.m, song_key)
                if not hashx:
                    print(
                        f'Error: Could not get the hash for the song key {song_key}')

                success = chord_node.save_key(hashx, song_value)
                if success:
                    print(f'Key {song_key} was saved in node {chord_node._id}')

            except:
                if not self.chord_successors_list:
                    print(
                        f'Error: Could not connect with chord node {self.chord_id}')
                    break


def main(address, spotify_address, chord_address, bits):
    host_ip, host_port = address.split(':')
    try:
        deamon = Pyro4.Daemon(host=host_ip, port=int(host_port))
    except:
        print('Error: There is another node in the system with that address, please try another')
        return

    spotify_node = SpotifyNode(address, chord_address, bits)
    uri = deamon.register(spotify_node)
    ns = Pyro4.locateNS()
    ns.register(f'SPOTIFY{address}', uri)

    if spotify_node.join(spotify_address):
        request_thread = threading.Thread(target=deamon.requestLoop)
        request_thread.start()

        chord_successor_list_thread = threading.Thread(
            target=spotify_node.update_chord_successor_list)
        chord_successor_list_thread.start()

        spotify_nodes_list_thread = threading.Thread(
            target=spotify_node.update_spotify_nodes_list)
        spotify_nodes_list_thread.start()

        print_thread = threading.Thread(target=spotify_node.print_node_info)
        print_thread.start()

    else:
        print(
            f'Error: Could not connect to the network, no spotify nodes with address: {spotify_address}')


if __name__ == '__main__':
    if len(sys.argv) == 4:
        main(sys.argv[1], None, sys.argv[2], int(sys.argv[3]))
    elif len(sys.argv) == 5:
        main(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]))
    else:
        print('Error: Missing arguments')
