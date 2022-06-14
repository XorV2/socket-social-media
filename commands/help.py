def help_command(client, username):
    client.send(
        f"""hello {username}, this is the command list:

    help -   this menu
    users -   see every user in the database
    view:username   -   view a users stats based on their username
    follow:username -    follow a user based on their username
    
    """.encode()
    )
