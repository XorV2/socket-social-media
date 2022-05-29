import json


def sign_up(
    client, client_address, functions: dict[str, object], consts: dict[str, object]
):
    LOGIN_FUNCS = consts["login_funcs"]
    WRONG_PASSWORD = consts["wrong_password"]

    open_file = functions["open_file"]
    contents = open_file("db", "users.json")
    register_page = functions["register_page"]
    write_to_file = functions["write_to_file"]

    client.send(b"Username(20 characters max) -> ")
    username = client.recv(20).decode()
    contents[username] = dict()

    client.sendall(b"Password(20 characters max) -> ")
    password = client.recv(20).decode()
    contents[username]["password"] = password

    contents = json.dumps(contents, indent=4)
    write_to_file("db", "users.json", contents, "w")

    client.send(b"Successfully signed up, please log in.")
    log_in(client, client_address, WRONG_PASSWORD, LOGIN_FUNCS)


def log_in(client, client_address, WRONG_PASSWORD, functions: dict[str, object]):
    main = functions["main"]
    open_file = functions["open_file"]
    register_page = functions["register_page"]
    write_to_file = functions["write_to_file"]
    check_credidentials = functions["check_credidentials"]
    check_client_address = functions["check_client_address"]

    if not check_client_address:
        client.close()
        return None

    users_r = open_file("db", "users.json")
    addresses_r = open_file("db", "addresses.json")

    client.send(b"Username -> ")
    username = client.recv(20).decode()

    client.send(b"Password -> ")
    password = client.recv(20).decode()

    are_valid = check_credidentials(username, password, open_file)

    if not are_valid[0]:
        if are_valid[1] == WRONG_PASSWORD:
            addresses_r[client_address] += 1

            content = json.dumps(addresses_r, indent=4)
            write_to_file("db", "addresses.json", content, "w")

        client.send(are_valid[1].encode())
        register_page(client, client_address)

    client.send(b"logged in successfully.")
    main(client, client_address, username)
