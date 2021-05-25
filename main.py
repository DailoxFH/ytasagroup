from flask import Flask, render_template, request, redirect, url_for, make_response, Response, send_from_directory
import string
import random

rooms = {}
app = Flask(__name__, static_url_path="/static", template_folder="templates", static_folder="static")

def generate_random(iter, lower=False):
    if lower:
        return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(iter))
    else:
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(iter))


def room_not_found():
    return Response("Room not found OR could not be created", status=404)


def username_not_found():
    return Response("Username not found", status=401)


def invalid_request():
    return Response("Invalid request", status=400)


def username_already_taken():
    return Response("Username already taken", status=401)


def check_if_room_exists(roomid):
    try:
        # noinspection PyStatementEffect
        rooms[roomid]
        return True
    except KeyError:
        return False


def check_cookie(cookies, cookie_values):
    where = 0
    avoid = []
    for i in range(0, len(cookies)):
        value = cookie_values[i]
        if value is None or value == '"' or value == "" or value == " ":
            avoid.append(i)
            continue
        else:
            where = i
    if len(avoid) == 0:
        avoid.append(where)
    return [where, avoid]


def get_id_from_link(input):
    if '/' in input:
        splittedUrl = input.split('/')
        return splittedUrl[-1].replace("watch?v=", "")
    else:
        return input


def create_cookie(roomId, username):
    resp = make_response(redirect(url_for("watchyt", roomid=roomId), code=307))
    id = generate_random(24, True)
    resp.set_cookie(username, id)
    rooms[roomId]["user"][username] = id
    return resp


def delete_cookies(roomId, cookies, avoid):
    resp = make_response(redirect(url_for("watchyt", roomid=roomId), code=307))
    for i in range(0, len(cookies)):
        if i not in avoid:
            resp.delete_cookie(list(cookies)[i])
            try:
                rooms.pop(list(cookies)[i])
            except KeyError:
                continue
        else:
            continue
    return resp


@app.route('/')
def sessions():
    return render_template('session.html')


@app.route("/watchyt", methods=["GET", "POST"])
def watchyt():
    try:
        roomId = request.args.get("roomid")
        if not check_if_room_exists(roomId):
            return room_not_found()
    except KeyError:
        return room_not_found()

    try:
        ytid = request.form["ytid"]
    except KeyError:
        ytid = rooms[roomId]["video"]["ytid"]

    yt_id = get_id_from_link(ytid)

    haveToDelete = False
    avoid = []
    cookie_keys = []
    where = 0
    try:
        cookie_keys = list(request.cookies.keys())
        cookie_values = list(request.cookies.values())
        check_cookie_ret = check_cookie(request.cookies, cookie_values)
        where = check_cookie_ret[0]
        avoid = check_cookie_ret[1]
        if len(list(cookie_keys)) > 1:
            return delete_cookies(roomId, request.cookies, avoid)
        # noinspection PyStatementEffect
        rooms[roomId]["user"][cookie_keys[where]] != cookie_values[where]
    except (KeyError, IndexError):
        try:
            username = request.form["username"]
            if username == "" or username.isspace():
                raise KeyError
            try:
                # noinspection PyStatementEffect
                rooms[roomId]["user"][username]
                return username_already_taken()
            except KeyError:
                return create_cookie(roomId, username)
        except KeyError:
            ret = 'Please provide a username: <br> <br>' \
                  f'<form action="/watchyt?roomid={roomId}" method="post">' \
                  '<input type="text" placeholder="Username" name="username" />' \
                  '<input type="submit"/>' \
                  '</form>'
            return ret

    # return str(cookie_keys)
    return render_template("watchyt.html", ytid=yt_id, roomId=roomId, user=cookie_keys[where])


@app.route("/generate_room", methods=["POST"])
def generate_room():
    global rooms
    try:
        ytid = request.form["ytid"]
        username = request.form["username"]
        if username == "":
            raise KeyError
    except KeyError:
        return room_not_found()

    roomId = generate_random(15)

    while roomId in rooms:
        roomId = generate_random(15)

    ytid = get_id_from_link(ytid)

    fullUpdate = {roomId: {"video": {"ytid": ytid, "event": "NOTHING", "time": 0.0, "doneBy": "NONE"}}}
    rooms.update(fullUpdate)

    rooms[roomId]["user"] = {}

    return create_cookie(roomId, username)


@app.route("/submit_text", methods=["GET"])
def submit_text():
    try:
        ytid = request.args.get("ytid")
        roomid = request.args.get("roomid")
        if not check_if_room_exists(roomid):
            return room_not_found()
        event = request.args.get("event")
        time = float(request.args.get("time"))
        cookie_keys = list(request.cookies.keys())
        cookie_values = list(request.cookies.values())
    except(KeyError, TypeError):
        return invalid_request()

    try:
        if rooms[roomid]["user"][cookie_keys[0]] == cookie_values[0]:
            eventToUpdate = convert(event)

            if rooms[roomid]["video"]["event"] == eventToUpdate:
                return "Rooms stay the same"

            rooms[roomid]["video"]["ytid"] = ytid
            rooms[roomid]["video"]["event"] = eventToUpdate
            rooms[roomid]["video"]["time"] = time

            if request.args.get("automaticallydone") == "true":
                if time == rooms[roomid]["video"]["time"]:
                    rooms[roomid]["video"]["doneBy"] = cookie_keys[0]
            else:
                rooms[roomid]["video"]["doneBy"] = cookie_keys[0]

            return "Rooms successfully updated"
        else:
            return username_not_found()
    except (KeyError, IndexError, TypeError):
        return username_not_found()


def convert(event):
    eventToUpdate = "NOTHING"
    try:
        event = int(event)
    except:
        return eventToUpdate
    if event == 0:
        eventToUpdate = "ENDED"
    elif event == 1:
        eventToUpdate = "PLAYING"
    elif event == 2:
        eventToUpdate = "PAUSED"
    elif event == 3:
        eventToUpdate = "BUFFERING"

    return eventToUpdate


@app.route("/changed", methods=["GET"])
def changed():
    try:
        roomid = request.args.get("roomid")
        if not check_if_room_exists(roomid):
            return room_not_found()
        event = request.args.get("event")
        ytid = request.args.get("ytid")
    except KeyError:
        return invalid_request()

    eventToCheck = convert(event)

    currentEvent = rooms[roomid]["video"]["event"]
    currentYtId = rooms[roomid]["video"]["ytid"]
    currentTime = rooms[roomid]["video"]["time"]
    currentDoneBy = rooms[roomid]["video"]["doneBy"]


    if currentEvent != eventToCheck or currentYtId != ytid:
        return {"status": "OUT", "video": currentYtId, "event": currentEvent, "time": currentTime, "doneBy": currentDoneBy}

    return {"status": "OK", "doneBy": currentDoneBy, "event": currentEvent, "time": currentTime}


@app.route("/js/<path:path>")
def send_js(path):
    return send_from_directory("js", path)


if __name__ == '__main__':
    from waitress import serve
    serve(app, port=5000)