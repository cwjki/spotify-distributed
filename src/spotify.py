from utils import hashing


class SpotifyNode:
    def __init__(self, address, chord_address, m) -> None:
        self.address = address
        self.chord_id = hashing(m, chord_address)
        self.chord_successors_list = []
        self.m = m
