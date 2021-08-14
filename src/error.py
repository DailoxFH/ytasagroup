from flask import Response, render_template


def room_not_found():
    return Response("Room not found OR could not be created", status=404)


def username_not_found():
    return Response("Username not found", status=401)


def invalid_request():
    return Response("Invalid request", status=400)


def username_already_taken(room_id):
    return render_template("username.html", room_id=room_id, already_taken=True)


def username_too_long():
    return Response("Username is too long. Please choose a shorter one", status=400)


def invalid_username():
    return Response("Invalid username. Please choose a different one", status=400)
