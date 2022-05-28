def sign_up(client, client_address, functions: dict[str, object]):
    register_page = functions["register_page"]
    open_file = functions["open_file"]
    contents = open_file("db", "users.json")

    client.send(b"Username(20 characters max) -> ")
    username = client.recv(20).decode()
    contents[username] = dict()

    client.sendall(b"Password(20 characters max) -> ")
    password = client.recv(20).decode()
    contents[username]["password"] = password

    client.send(b"Successfully signed up, please log in.")
    register_page(client, client_address)


def log_in():
    ...
