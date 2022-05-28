def help_command(client, username):
    client.send(
        f"""hello {username}, this is the command list:

    help - this menu
    ... - ...
    ... - ...
    
    """.encode()
    )
