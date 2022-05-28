def check_credidentials(username, password, open_file):
    contents = open_file("db", "users.json")

    if username not in contents:
        return [False, "username doesn't exist"]

    if password != contents[username]["password"]:
        return [False, "password doesn't match the username"]

    return [True]
