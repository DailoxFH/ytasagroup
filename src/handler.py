from flask import Flask, render_template, request, send_from_directory
from src import error
from src import cookies
from src import generator
from shared_memory_dict import SharedMemoryDict

rooms = SharedMemoryDict(name='rooms', size=1049000)

app = Flask(__name__, static_url_path="/static", template_folder="../templates", static_folder="../static")


@app.route('/')
def sessions():
    return render_template('session.html')


def update_rooms(room_id, user_to_add, video_to_add):
    video = rooms[room_id]["video"]
    user = rooms[room_id]["user"]

    video = generator.update_dict(video, video_to_add)
    user = generator.update_dict(user, user_to_add)

    full_update = {room_id: {"video": video, "user": user}}
    rooms.update(full_update)


def create_cookie(room_id, username):
    cookie_ret = cookies.create_cookie(room_id, username)
    resp = cookie_ret[0]
    removed_username = cookie_ret[1]
    if len(removed_username) >= 26:
        return error.username_too_long()
    val = cookie_ret[2]

    update_rooms(room_id, {removed_username: val}, {"joined": True})
    return resp


@app.route("/watch_yt", methods=["GET", "POST"])
def watch_yt():
    try:
        room_id = request.args.get("roomid")
        if not generator.check_if_room_exists(rooms, room_id):
            return error.room_not_found()
    except KeyError:
        return error.room_not_found()

    try:
        yt_id = request.form["ytid"]
    except KeyError:
        yt_id = rooms[room_id]["video"]["ytid"]

    yt_id = generator.get_id_from_link(yt_id)
    if not yt_id:
        return error.invalid_request()
    try:
        where = cookies.check_cookie(rooms, request.cookies, room_id)
        # noinspection PyStatementEffect
        rooms[room_id]["user"][where] != request.cookies[where]
    except (KeyError, IndexError):
        try:
            username = request.form["username"]
            if username == "" or username.isspace():
                raise KeyError
            try:
                # noinspection PyStatementEffect
                rooms[room_id]["user"][username]
                return error.username_already_taken()
            except KeyError:
                return create_cookie(room_id, username)
        except KeyError:
            return render_template("username.html", room_id=room_id, already_taken="")

    return render_template("watchyt.html", ytid=yt_id, roomId=room_id, user=where)


@app.route("/generate_room", methods=["POST"])
def generate_room():
    global rooms
    try:
        yt_id = request.form["ytid"]
        username = request.form["username"]
        if username == "":
            raise KeyError
    except KeyError:
        return error.room_not_found()

    room_id = generator.generate_random(15)

    while room_id in rooms:
        room_id = generator.generate_random(15)

    yt_id = generator.get_id_from_link(yt_id)

    full_update = {room_id: {"video": {"ytid": yt_id, "event": "NOTHING", "time": 0.0, "doneBy": "NONE"}, "user": {}}}
    rooms.update(full_update)

    return create_cookie(room_id, username)


@app.route("/submit_text", methods=["GET"])
def submit_text():
    try:
        yt_id = generator.get_id_from_link(request.args.get("ytid"))
        if not yt_id:
            return error.invalid_request()
        room_id = request.args.get("roomid")
        if not generator.check_if_room_exists(rooms, room_id):
            return error.room_not_found()
        event = request.args.get("event")
        try:
            time = float(request.args.get("time"))
        except ValueError:
            return error.invalid_request()
        list(request.cookies.keys())
        list(request.cookies.values())
    except(KeyError, TypeError):
        return error.invalid_request()

    try:
        where = cookies.check_cookie(rooms, request.cookies, room_id)
        hashed_value = cookies.hashlib.sha512(request.cookies[where].encode())
        if rooms[room_id]["user"][where] == hashed_value.hexdigest():
            event_to_update = generator.convert(event)

            if rooms[room_id]["video"]["event"] == event_to_update and rooms[room_id]["video"]["ytid"] == yt_id:
                return {"status": "Rooms stay the same"}

            update_rooms(room_id, None, {"ytid": yt_id, "event": event_to_update, "time": time, "doneBy": where, "joined": False})
            return {"status": "OK", "ytid": yt_id}
        else:
            return error.username_not_found()
    except (KeyError, IndexError, TypeError):
        return error.username_not_found()


@app.route("/changed", methods=["GET"])
def changed():
    try:
        room_id = request.args.get("roomid")
        if not generator.check_if_room_exists(rooms, room_id):
            return error.room_not_found()
        event = request.args.get("event")
        yt_id = generator.get_id_from_link(request.args.get("ytid"))
        if not yt_id:
            return error.invalid_request()
    except KeyError:
        return error.invalid_request()

    event_to_check = generator.convert(event)

    current_event = rooms[room_id]["video"]["event"]
    current_yt_id = rooms[room_id]["video"]["ytid"]
    current_time = rooms[room_id]["video"]["time"]
    current_done_by = rooms[room_id]["video"]["doneBy"]

    if current_event != event_to_check or current_yt_id != yt_id:
        return {"status": "OUT", "video": current_yt_id, "event": current_event, "time": current_time, "doneBy": current_done_by}

    return {"status": "OK", "doneBy": current_done_by, "event": current_event, "time": current_time, "video": current_yt_id, "joined": rooms[room_id]["video"]["joined"]}


@app.route("/js/<path:path>")
def send_js(path):
    return send_from_directory("js", path)


@app.route("/css/<path:path>")
def send_css(path):
    return send_from_directory("css", path)


def get_app():
    return app
