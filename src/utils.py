import Pyro4
import hashlib


def hashing(bits, string):
    try:
        hashx = hashlib.sha256(string.encode('utf-8', 'ignore')).hexdigest()
        hashx = int(hashx, 16) % pow(2, bits)
        return hashx
    except:
        return None


def get_node_instance(idx):
    return get_proxy(f'CHORD:{idx}')


def get_proxy(idx):
    Pyro4.Proxy(f'PYRONAME:{idx}')
    with Pyro4.Proxy(f'PYRONAME:{idx}') as p:
        try:
            p._pyroBind()
            return p
        except:
            return None
