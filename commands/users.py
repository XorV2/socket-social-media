def users_command(client, functions: dict[str, object]):
    open_file: object = functions["open_file"]
    users = open_file("db", "users.json")
    to_output = ""

    for each_user in users:
        to_output += f"  {each_user}\n"

    client.send(to_output.encode())
