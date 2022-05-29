import json


class priv_funcs:
    @staticmethod
    def _check(command):
        try:
            user_to_unfollow = command.split(":")[1]
        except:
            return {"is_split": False}
        else:
            return {"is_split": True, "user_to_unfollow": user_to_unfollow}

    @staticmethod
    def _check_db(content, file, mode="in"):
        if mode == "in":
            if content in file:
                return True
            return False


def unfollow_command(client, username, command, functions: dict[str, object]):
    open_file = functions["open_file"]
    write_to_file = functions["write_to_file"]

    users = open_file("db", "users.json")
    checked_info = priv_funcs._check(command)

    if not checked_info["is_split"]:
        client.send(b"Please use this format, follow:username")
        return None

    user_to_unfollow = checked_info["user_to_unfollow"]

    if not priv_funcs._check_db(user_to_unfollow, users, "in"):
        client.send(b"Sorry, you cant unfollow a user that doesnt exist")
        return None

    client_following = users[username]["stats"]["following"]

    if not priv_funcs._check_db(user_to_unfollow, client_following[1], "in"):
        client.send(b"Sorry, you cant unfollow someone youre not following")

    users[username]["stats"]["following"]["amount"] += 1
    users[username]["stats"]["following"]["usernames"].remove(user_to_unfollow)

    users[user_to_unfollow]["stats"]["followers"]["amount"] -= 1
    users[user_to_unfollow]["stats"]["followers"]["usernames"].remove(username)

    content = json.dumps(users, indent=4)
    write_to_file("db", "users.json", users)
