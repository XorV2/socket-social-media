import json
import socket
import inspect
import threading
from warnings import filterwarnings

# import functions which could potentially be modified in the future
from commands.help import help_command
from commands.users import users_command

from db.user import sign_up, log_in
from db.check import check_credidentials


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

    if client_address in blacklists:
        client.close()
        return -1

    client.send(b"signup or login ->")
    command = client.recv(6).decode()

    if command == "signup":
        sign_up(
            client,
            client_address,
            LOGIN_FUNCS,
            {"login_funcs": LOGIN_FUNCS, "wrong_password": WRONG_PASSWORD},
        )

    elif command == "login":
        log_in(client, client_address, WRONG_PASSWORD, LOGIN_FUNCS)

    else:
        client.send(b"Please enter 'signup' or 'login'.")
        register_page(client, client_address)


SIGNUP_FUNCS = {"open_file": open_file, "register_page": register_page}

LOGIN_FUNCS = {
    "main": main,
    "open_file": open_file,
    "register_page": register_page,
    "write_to_file": write_to_file,
    "check_credidentials": check_credidentials,
    "check_client_address": check_client_address,
}

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
