"""
This code sucks to read, and look gross
i'll fix this...
...
...
..
.
eventually...
"""


def _check(command):
    """
    this functions purpose is to check that the command can be split with :
    if it can, return [True, split_command], if not, return [False]
    """
    try:
        username = command.split(":")[1]
    except:
        return [False]
    else:
        return [True, username]


def view_command(client, command, open_file: object):
    users = open_file("db", "users.json")

    split_command = _check(command)
    if not split_command[0]:
        client.send(b"Please use this format, view:username")
        return None

    user_to_view = split_command[1]

    if user_to_view not in users:
        client.send(f"User {user_to_view} does not exist.".encode())
        return None

    info_about_user = users[user_to_view]["stats"]
    info_formatted = f"""
    {user_to_view}:
        followers - {info_about_user["followers"]["amount"]}
        following - {info_about_user["following"]["amount"]}

    """
    client.send(str(info_formatted).encode())
