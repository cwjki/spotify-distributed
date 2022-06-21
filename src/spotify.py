import sys
import threading
from urllib import request
import Pyro4
from utils import hashing, get_spotify_node_instance


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
