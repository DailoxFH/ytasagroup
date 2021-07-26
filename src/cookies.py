from flask import make_response, redirect, url_for
import hashlib
from src.generator import generate_random


def create_cookie(room_id, username):
    resp = make_response(redirect(url_for("watch_yt", roomid=room_id), code=307))
    id = generate_random(24, True)
    resp.set_cookie(username, id)
    h = hashlib.sha512(id.encode())
    return [resp, h.hexdigest()]


def check_cookie(rooms, cookies, room_id):
    where = ""
    for i in range(0, len(cookies)):
        for k, v in cookies.items():
            if k in rooms[room_id]["user"].keys():
                where = k
    return where
