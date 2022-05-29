import json


def _check(command):
    """
    the purpose of this function is to see if the command can be split by :
    if it can, return [True, user_to_follow], if not, return [False]
    """

    try:
        user_to_follow = command.split(":")[1]
    except:
        return [False]
    else:
        return [True, user_to_follow]


def _check_db(content, file, mode="in"):
    if mode == "in":
        if content in file:
            return True
        return False


def follow_command(client, username, command, functions: dict[str, object]):
    open_file = functions["open_file"]
    write_to_file = functions["write_to_file"]

    users = open_file("db", "users.json")
    split_command = _check(command)

    if not split_command[0]:
        client.send(b"Please use this format, follow:username")
        return None

    user_to_follow = split_command[1]

    if not _check_db(user_to_follow, users, "in"):
        client.send(b"User does not exist.")
        return None

    client_following = users[username]["stats"]["following"]
    user_followers = users[user_to_follow]["stats"]["followers"]
    # this is a bit of a jumble, fix it.

    if _check_db(user_to_follow, client_following[1], "in"):
        client.send(b"you are already following this user.".encode())
        return None

    """
    add one to the clients following and append the person who the user who
    they followed to the list of people who they follow.

    then add one to the followed users followers and append the user who
    followed them into their list of people who follow them.
    """
    users[username]["stats"]["following"][0] += 1
    users[username]["stats"]["following"][1].append(user_to_follow)

    users[user_to_follow]["stats"]["followers"][0] += 1
    users[user_to_follow]["stats"]["followers"][1].append(username)

    content = json.dumps(users, indent=4)

    write_to_file("db", "users.json", content, "w")
