def view_command(client, command, open_file):
    users = open_file("db", "users.json")

    try:
        user_to_view = command.split(":")[1]
    except:
        client.send(b"Please use this format, view:username")
    else:
        if user_to_view in users:
            info_about_viewed_user = users[user_to_view]
            client.send(info_about_viewed_user.encode())
            return None
        client.send(f"User {user_to_view} does not exist.".encode())
