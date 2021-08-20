import string
import random
from urllib.parse import unquote


def generate_random(iterations, lower=False):
    if lower:
        return ''.join(
            random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(iterations))
    else:
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(iterations))


def get_id_from_link(link):
    to_check = ["/watch?v=", "/embed/", "/v/", "youtu.be"]
    if any(substring in link for substring in to_check):
        splitted_url = link.split('/')
        return splitted_url[-1].replace("watch?v=", "")
    elif len(link) == 11 and '/' not in link:
        return link
    else:
        return False


def convert(event):
    event_to_update = "NOTHING"
    try:
        event = int(event)
    except:
        return event_to_update
    if event == 0:
        event_to_update = "ENDED"
    elif event == 1:
        event_to_update = "PLAYING"
    elif event == 2:
        event_to_update = "PAUSED"
    elif event == 3:
        event_to_update = "BUFFERING"

    return event_to_update


def check_if_room_exists(rooms, roomid):
    try:
        # noinspection PyStatementEffect
        rooms[roomid]
        return True
    except KeyError:
        return False


def update_dict(base_dict, to_add):
    try:
        for k, v in to_add.items():
            base_dict.__setitem__(k, v)
    except AttributeError:
        return base_dict
    return base_dict


def unquote_cookies(cookie_dict):
    new_cookies = {}
    for k, v in cookie_dict.items():
        new_cookies[unquote(k)] = v

    return new_cookies
