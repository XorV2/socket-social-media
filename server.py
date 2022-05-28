import json
import socket
import inspect
import threading
from warnings import filterwarnings
from commands.help import help_command
from commands.users import users_command


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
FILE_NAMES = {"users.json", "blacklists.json", "addresses.json"}
WRONG_PASSWORD = "password doesn't match the username"
filterwarnings("ignore", category=DeprecationWarning)


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
    register_page(client, client_address)


# -----------------
def check_client_address(client_address):
    addresses_r = open_file("db", "addresses.json")

    if not (client_address in addresses_r):
        addresses_r[client_address] = {"chances": 0}
        content = json.dumps(addresses_r, indent=4)

        write_to_file("db", "addresses.json", content, "w")
        return True

    chances = addresses_r[client_address]["chances"]

    if chances == 3:
        return False
    return True


# -----------------
def login_client(client, client_address, blacklists):
    if not check_client_address:
        client.close()
        return None
    
    addresses_r = open_file("db", "addresses.json")
    users_r = open_file("db", "users.json")

    client.send(b"Username -> ")
    username = client.recv(20).decode()

    client.send(b"Password -> ")
    password = client.recv(20).decode()

    are_valid = check_credidentials(username, password)

    if not are_valid[0]:
        if are_valid[1] == WRONG_PASSWORD:
            clients_chances += 1

            content = json.dumps(addresses_r, indent=4)
            write_to_file("db", "addresses.json", content, "w")

        client.send(are_valid[1].encode())
        register_page(client, client_address)

    client.send(b"logged in successfully.")
    main(client, client_address, username)


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


def register_page(client, client_address):
    blacklists = open_file("db", "blacklists.json")
    contents = open_file("db", "users.json")

    if client_address in blacklists:
        client.close()
        return -1

    client.send(b"signup or login ->")
    command = client.recv(6).decode()

    if command == "signup":
        signup_client(contents)

    elif command == "login":
        login_client(client, client_address, blacklists)

    else:
        client.send(b"Please enter 'signup' or 'login'.")
        register_page(client, client_address)


"""
check if users.json, blacklists.json and addresses.json exist
if they don't, create them
"""

for file_name in FILE_NAMES:
    try:
        open_file("db", file_name)
    except:
        write_to_file("db", file_name, {})
        # write_to_file creates the file for you if it doesn't exist


if __name__ == "__main__":
    s = socket.socket()
    s.bind(("0.0.0.0", 8000))
    s.listen(2)

    while True:
        client, client_address = s.accept()
        print(f"{client_address} accepted.")
        threading.Thread(target=register_page(client, client_address[0])).start()
