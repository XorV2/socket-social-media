import socket
import threading
import json
import inspect
from warnings import filterwarnings

"""
the inspect module is the only one i am going to document because i'm not
familiar with it and i would assume that alot of other people aren't as
well

the inspect module is the one i'm using for my command handling, as my
functions take different parameters depending on what the point of the
function is

this module is used to get the parameters in which will be taken by the
function before i have to run it so instead of having to give all of my
functions the same parameters i can just get the parameters from the module.
"""
filterwarnings("ignore", category=DeprecationWarning)

# -----------------
def help(client, username):
    client.send(
        f"""hello {username}, this is the command list:

    help - this menu
    ... - ...
    ... - ...
    
    """.encode()
    )


# -----------------
def open_file(path, file_name):
    with open(f"{path}/{file_name}", "r") as f:
        opened_file = json.load(f)

    return opened_file


# -----------------
def write_to_file(path, file_name, content, mode="a"):
    """
    default mode set to append in-case file doesn't exist.
    """
    with open(f"{path}/{file_name}", mode) as f:
        f.write(content)


# -----------------
def check_credidentials(username, password):
    contents = open_file("db", "users.json")

    if username not in contents:
        return [False, "username doesn't exist"]

    if password != contents[username]["password"]:
        return [False, "password doesn't match the username"]

    return [True]


# -----------------
def signup_client(contents):
    client.send(b"Username(20 characters max) -> ")
    username = client.recv(20).decode()
    contents[username] = dict()
    """
    receive a maximum of 20 bytes from the client and decoding it
    storing it in the database as the username, same with the password
    """

    client.sendall(b"Password(20 characters max) -> ")
    password = client.recv(20).decode()
    contents[username]["password"] = password

    data = open_file("db", "users.json")

    client.send(b"Successfully signed up, please log in.")
    login_client(client, client_address)


# -----------------
def login_client(blacklists):
    addresses_r = open_file("db", "addresses.json")
    users_r = open_file("db", "users.json")

    if client_address not in addresses_r:
        addresses_r[client_address], chances = 0, 0
        content = json.dumps(addresses_r, indent=4)
        write_to_file("db", "addresses.json", content, "w")

    else:
        chances = addresses_r[client_address]
        if chances == 3:
            blacklists[client_address] = 1
            content = json.dumps(blacklists, indent=4)
            write_to_file("db", "blacklisted.json", content, "w")

    client.send(b"Username -> ")
    username = client.recv(20).decode()

    if username not in users_r:
        client.send(b"Username invalid, try again.")
        login_client(client, client_address)
        return None

    client.send(b"Password -> ")
    password = client.recv(20).decode()

    if password != users_r[username]["password"]:
        addresses_r[client_address] += 1
        content = json.dumps(addresses_r, indent=4)
        write_to_file("db", "addresses.json", content, "w")

        client.send(b"Password invalid.")
        login_client(client, client_address)
        return None

    client.send(b"logged in successfully.")
    main(client, client_address, username)


# -----------------
def users_command(client, file):
    ...


# -----------------
def help_command(client, username):
    client.send(
        f"""hello {username}, this is the command list:

    help - this menu
    ... - ...
    ... - ...
    
    """.encode()
    )


# -----------------


def main(client, client_address, username):
    """
    the main function is for handling clients who have now logged in
    handling their traffic and allowing them to give commands
    """

    print(f"{client_address} has logged in.")

    commands = {"help": help_command, "users": users_command}
    file = open_file("db", "users.json")

    while True:
        client.send(f"[{username}] -> ".encode())
        command = client.recv(50).decode()
        print(f"[{username}] {command}")

        try:
            func = commands[command]
        except:
            client.send(b"Invalid command. Type help for help\n")
        else:
            params = inspect.getargspec(func)[0]
            func(client, params[1])


def login_client(client, client_address):
    try:
        blacklists = open_file("db", "blacklists.json")
    except:
        write_to_file("db", "blacklists.json", {})
        login_client(client, client_address)

    if client_address in blacklists:
        client.close()
        return -1

    try:
        contents = open_file("db", "users.json")
    except:
        write_to_file("db", "blacklists.json", {})
        login_client(client, client_address)

    client.send(b"signup or login ->")
    command = client.recv(6).decode()

    if command == "signup":
        contents = open_file("db", "users.json")
        signup_client(contents)

    elif command == "login":
        blacklists = open_file("db", "blacklists.json")
        login_client(blacklists)

    else:
        client.send('Please enter "signup" or "login".')
        login_client(client, client_address)


if __name__ == "__main__":
    s = socket.socket()
    s.bind(("0.0.0.0", 8000))
    s.listen(2)

    while True:
        client, client_address = s.accept()
        print(client_address)
        print(f"{client_address} accepted.")
        threading.Thread(target=login_client(client, client_address[0])).start()
