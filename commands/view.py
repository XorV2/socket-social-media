"""
Update this function to allow that
'password':'somepassword'

doesn't exist and it shows the stats of the user.
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


def view_command(client, command, open_file):
    users = open_file("db", "users.json")

    split_command = _check(command)
    if not split_command[0]:
        client.send(b"Please use this format, view:username")
        return None

    user_to_view = split_command[1]

    if user_to_view not in users:
        client.send(f"User {user_to_view} does not exist.".encode())
        return None

    info_about_user = users[user_to_view]
    client.send(str(info_about_user).encode())
