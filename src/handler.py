import shared_memory_dict.hooks
from flask import Flask, render_template, request, send_from_directory
from src import error
from src import cookies
from src import generator
from shared_memory_dict import SharedMemoryDict
import atexit

rooms = SharedMemoryDict(name='rooms', size=1049000)

app = Flask(__name__, static_url_path="/static", template_folder="../templates", static_folder="../static")


@app.route('/')
def sessions():
    return render_template('session.html')


def update_rooms(room_id, user_to_add=None, video_to_add=None, delete=""):
    base_video = rooms[room_id]["video"]
    base_user = rooms[room_id]["user"]

    if not delete and video_to_add is not None:
        base_video = generator.update_dict(base_video, video_to_add)
    if not delete and user_to_add is not None:
        base_user = generator.update_dict(base_user, user_to_add)
    elif delete:
        if video_to_add is not None:
            del base_video[delete]
        if user_to_add is not None:
            del base_user[delete]
    else:
        del rooms[room_id]
        return

    full_update = {room_id: {"video": base_video, "user": base_user}}
    rooms.update(full_update)


def check_user(room_id, request_cookies=None):
    if request_cookies is None:
        request_cookies = request.cookies

    all_hashed_values = []
    for k, v in request.cookies.items():
        all_hashed_values.append(cookies.hashlib.sha512(request_cookies[k].encode()).hexdigest())
    where = cookies.check_cookie(rooms, request_cookies, room_id, all_hashed_values)
    hashed_value = cookies.hashlib.sha512(generator.unquote_cookies(request_cookies)[where].encode())
    password = rooms[room_id]["user"][where]["password"]
    if password == hashed_value.hexdigest():
        return {"status": True, "where": where, "password": password}
    else:
        return {"status": False}


def create_cookie(room_id, username):
    cookie_ret = cookies.create_cookie(room_id, username)
    resp = cookie_ret[0]
    removed_username = cookie_ret[1]
    if removed_username is None:
        return error.username_too_long(room_id)
    if not removed_username or removed_username.isspace():
        return error.invalid_username(room_id)
    val = cookie_ret[2]

    try:
        temp_joined = rooms[room_id]["video"]["joined"]
    except KeyError:
        temp_joined = []

    temp_joined.append(removed_username)

    update_rooms(room_id, user_to_add={removed_username: {"password": val}}, video_to_add={"joined": temp_joined})

    return resp


def get_all_users_in_room(room_id):
    to_ret = []

    for k, v in rooms[room_id]["user"].items():
        to_ret.append(k)

    return to_ret


@app.route("/watch_yt", methods=["GET", "POST"])
def watch_yt():
    try:
        room_id = cookies.escape(request.args.get("roomid"))
        if not generator.check_if_room_exists(rooms, room_id):
            raise KeyError
    except KeyError:
        return error.room_not_found()

    try:
        yt_id = request.form["ytid"]
    except KeyError:
        yt_id = rooms[room_id]["video"]["ytid"]

    yt_id = generator.get_id_from_link(yt_id)
    if not yt_id:
        return error.invalid_request("username.html")
    try:
        check_user_ret = check_user(room_id)
        if check_user_ret["status"]:
            where = check_user_ret["where"]
            # noinspection PyStatementEffect
            rooms[room_id]["user"][where] != generator.unquote_cookies(request.cookies)[where]
        else:
            raise KeyError
    except (KeyError, IndexError):
        try:
            username = cookies.escape(request.form["username"])
        except KeyError:
            return render_template("username.html", room_id=room_id, already_taken=False)

        if not username or username.isspace():
            return error.invalid_username(room_id)

        try:
            # noinspection PyStatementEffect
            rooms[room_id]["user"][username]
            return error.username_already_taken(room_id)
        except KeyError:
            return create_cookie(room_id, username)

    return render_template("watchyt.html", ytid=yt_id, roomId=room_id, user=where)


@app.route("/generate_room", methods=["POST"])
def generate_room():
    global rooms
    try:
        yt_id = cookies.escape(request.form["ytid"])
        username = cookies.escape(request.form["username"])
        if not username:
            raise KeyError
    except KeyError:
        return error.room_not_found()

    room_id = generator.generate_random(15)

    while room_id in rooms:
        room_id = generator.generate_random(15)

    yt_id = generator.get_id_from_link(yt_id)
    if not yt_id:
        return error.invalid_request("session.html")

    full_update = {room_id: {"video": {"ytid": yt_id, "event": "NOTHING", "time": 0.0, "doneBy": "NONE"}, "user": {}}}
    rooms.update(full_update)
    return create_cookie(room_id, username)


@app.route("/submit_text", methods=["GET"])
def submit_text():
    try:
        room_id = cookies.escape(request.args.get("roomid"))
        if not generator.check_if_room_exists(rooms, room_id):
            return error.room_not_found()
        yt_id = generator.get_id_from_link(request.args.get("ytid"))
        if not yt_id:
            return error.invalid_request(message=rooms[room_id]["video"]["ytid"])
        event = request.args.get("event")
        try:
            time = float(request.args.get("time"))
        except ValueError:
            return error.invalid_request("error.html")
        list(request.cookies.keys())
        list(request.cookies.values())
    except(KeyError, TypeError):
        return error.invalid_request("error.html")

    try:
        check_user_ret = check_user(room_id)
        if check_user_ret["status"]:
            event_to_update = generator.convert(event)
            stay_done_by = check_user_ret["where"]

            if rooms[room_id]["video"]["event"] == event_to_update and rooms[room_id]["video"]["ytid"] == yt_id:
                stay_done_by = rooms[room_id]["video"]["doneBy"]
                time = rooms[room_id]["video"]["time"]

            username = check_user_ret["where"]
            yt_id = cookies.escape(yt_id)
            update_rooms(room_id,
                         user_to_add={
                             username: {"password": check_user_ret["password"]}},
                         video_to_add={"ytid": yt_id, "event": event_to_update, "time": time, "doneBy": stay_done_by})

            return {"status": "OK", "ytid": yt_id}
        else:
            return error.username_not_found()
    except (KeyError, IndexError, TypeError) as e:
        return error.username_not_found()


@app.route("/changed", methods=["GET"])
def changed():
    try:
        room_id = cookies.escape(request.args.get("roomid"))
        if not generator.check_if_room_exists(rooms, room_id):
            return error.room_not_found()
        event = request.args.get("event")
        yt_id = generator.get_id_from_link(request.args.get("ytid"))
        if not yt_id:
            return error.invalid_request(message=rooms[room_id]["video"]["ytid"])
    except KeyError:
        return error.invalid_request("error.html")

    try:
        check_user_ret = check_user(room_id)
        if check_user_ret["status"]:
            event_to_check = generator.convert(event)

            current_event = rooms[room_id]["video"]["event"]
            current_yt_id = rooms[room_id]["video"]["ytid"]
            current_time = rooms[room_id]["video"]["time"]
            current_done_by = rooms[room_id]["video"]["doneBy"]

            status = "OK"
            if current_event != event_to_check or current_yt_id != yt_id:
                status = "OUT"

            return {"status": status, "doneBy": current_done_by, "event": current_event, "time": current_time,
                    "video": current_yt_id,
                    "allUsers": get_all_users_in_room(room_id)}
        else:
            return error.username_not_found()
    except (KeyError, IndexError, TypeError):
        return error.username_not_found()


@app.route("/disconnect", methods=["GET"])
def disconnect():
    try:
        room_id = cookies.escape(request.args.get("roomid"))
        if not generator.check_if_room_exists(rooms, room_id):
            return error.room_not_found()
    except KeyError:
        return error.invalid_request("error.html")

    request_cookies = request.cookies
    check_user_ret = check_user(room_id, request_cookies)
    if check_user_ret["status"]:
        if len(rooms[room_id]["user"].keys()) <= 1:
            update_rooms(room_id)
        else:
            update_rooms(room_id, user_to_add={}, delete=check_user_ret["where"])
        return "Success"
    else:
        return error.username_not_found()


@app.route("/js/<path:path>")
def send_js(path):
    return send_from_directory("js", path)


@app.route("/css/<path:path>")
def send_css(path):
    return send_from_directory("css", path)


def get_app():
    return app


def cleanup():
    rooms.cleanup()
    shared_memory_dict.hooks.free_shared_memory("rooms")


atexit.register(cleanup)
