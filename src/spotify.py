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
                    spotify_nodes = self.spotify_nodes_list
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
