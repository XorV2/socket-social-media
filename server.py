import json
import socket
import threading

# import functions which could potentially be modified in the future
from commands.follow import follow_command
from commands.help import help_command
from commands.unfollow import unfollow_command
from commands.users import users_command
from commands.view import view_command

from db.check import check_credidentials
from db.user import log_in, sign_up

FILE_NAMES = {"users.json", "blacklists.json", "addresses.json"}
WRONG_PASSWORD = "password doesn't match the username"
CLIENT_ERROR = WindowsError


# -----------------
def open_file(path, file_name):
    """
    this function opens a file and returns the opened file allowing
    to read it

    the parameters path and file_name exist for flexibility.
    """
    with open(f"{path}/{file_name}", "r") as f:
        opened_file = json.load(f)

    return opened_file


# -----------------
def write_to_file(path, file_name, content, mode="a"):
    """
    this function simply writes to a file, the parameters path, file_name
    allow for flexibility in-case they change.

    default mode set to append in-case file doesn't exist.
    """
    with open(f"{path}/{file_name}", mode) as f:
        f.write(str(content))


# -----------------
def check_client_address(username, client_address):
    """
    reminder to self:

    updating the addresses.json file to have the username in it so that i can
    create a chat room between two users and send the request to the user in
    which they are requesting to chat with

    this is for ease of use because

    chat:username

    is better than

    chat:ipaddr

    DNS proves this.
    """

    addresses_r = open_file("db", "addresses.json")

    if username not in addresses_r:
        addresses_r[username] = {"client_address": client_address, "chances": 0}
        content = json.dumps(addresses_r, indent=4)

        write_to_file("db", "addresses.json", content, "w")
        return True

    chances = addresses_r[username]["chances"]

    if chances == 3:
        return False
    return True


# -----------------
def main(client, client_address, username):
    """
    the main function is for handling clients who have now logged in
    handling their traffic and allowing them to give commands
    """

    try:
        # now there are some errors with this which i will address in readMe.md
        if check_client_address(username, client_address) == False:
            client.send(b"You have been blacklisted.")

        print(f"{client_address} has logged in.")

        while True:
            client.send(f"[{username}] -> ".encode())
            command = client.recv(50).decode()
            print(f"[{username}] {command}")

            if command == "help":
                help_command(client, username)

            elif command == "users":
                users_command(client, {"open_file": open_file})

            elif "view" in command:
                view_command(client, command, open_file)

            elif "unfollow" in command:
                unfollow_command(
                    client,
                    username,
                    command,
                    {"open_file": open_file, "write_to_file": write_to_file},
                )

            elif "follow" in command:
                follow_command(
                    client,
                    username,
                    command,
                    {"open_file": open_file, "write_to_file": write_to_file},
                )

            else:
                client.send(b"Invalid command.")
    except CLIENT_ERROR:
        print(f"{client_address} Threw an error.")


# -----------------
def register_page(client, client_address):
    """
    The page where you register,

    signup or login -> signup

    username -> ...
    password -> ...

    this then redirects you to the login page

    username -> ...
    password -> ...

    ...
    """
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
