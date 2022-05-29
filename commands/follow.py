import json


class priv_funcs:
    @staticmethod
    def _check(command):
        try:
            user_to_follow = command.split(":")[1]
        except:
            return {"is_split": False}
        else:
            return {"is_split": True, "user_to_follow": user_to_follow}

    @staticmethod
    def _check_db(content, file, mode="in"):
        if mode == "in":
            if content in file:
                return True
            return False


def follow_command(client, username, command, functions: dict[str, object]):
    open_file = functions["open_file"]
    write_to_file = functions["write_to_file"]

    users = open_file("db", "users.json")
    checked_info = priv_funcs._check(command)

    if not checked_info["is_split"]:
        client.send(b"Please use this format, follow:username")
        return None

    user_to_follow = checked_info["user_to_follow"]

    if not priv_funcs._check_db(user_to_follow, users, "in"):
        client.send(b"User does not exist.")
        return None

    client_following = users[username]["stats"]["following"]
    # this is a bit of a jumble, fix it.

    if priv_funcs._check_db(user_to_follow, client_following["usernames"], "in"):
        client.send(b"you are already following this user.".encode())
        return None

    """
    add one to the clients following and append the person who the user who
    they followed to the list of people who they follow.

    then add one to the followed users followers and append the user who
    followed them into their list of people who follow them.
    """
    users[username]["stats"]["following"]["amount"] += 1
    users[username]["stats"]["following"]["usernames"].append(user_to_follow)

    users[user_to_follow]["stats"]["followers"]["amount"] += 1
    users[user_to_follow]["stats"]["followers"]["usernames"].append(username)

    content = json.dumps(users, indent=4)
    write_to_file("db", "users.json", content, "w")
