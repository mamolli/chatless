
def stem(s):
    diactrit_map = {'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z', 'ł': 'l', 'ą': 'a', 'ę': 'e', 'ń': 'n', 'ć': 'c'}
    s = ''.join((diactrit_map.get(char, char) for char in s))
    return s.strip().lower()

def list_comibination(item_id, item_name):
    item_name = stem(item_name)
    return (str(item_id), item_name, f'${item_id} {item_name}', f'${item_id}')

def get_free_id(ids):
    ids = sorted(ids)
    range_end = int(ids[-1]) + 2 if ids else 1
    for n in range(range_end):
        # this could be done with o(n) or even less...
        if n not in ids:
            return n
    raise StopIteration