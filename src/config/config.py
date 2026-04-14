import os
from os import getenv
from dotenv import load_dotenv

load_dotenv()

class bot:
    token = getenv("DISCORD_TOKEN")
    default_prefix = '!'
    api = True
    owner_ids = {int(x.strip()) for x in getenv("OWNER_ID", "").split(",") if x.strip()}
    default_status = "CFC bot"
    cogs = [
        "tools",
        "voice",
        "jishaku",
        "dev",
        "events"
    ]

    # Get current working directory
    current_dir = os.getcwd()

    # Build path to "cogs" inside parent
    cogs_path = os.path.join(current_dir, "src/cogs")

    # List of files/folders to exclude
    exclude = {"__pycache__", "__init__.py"}

    for command in os.listdir(cogs_path):

        full_path = os.path.join(cogs_path, command)

        if not os.path.isdir(full_path):
            continue

        if command in exclude:
            continue        

        if command not in cogs:
            cogs.append(command)

    support_invite = "https://discord.gg/dn2dpgCbXP"
    invite_link = ""
    vote_link = ""
    website = "https://codersforcoders.xyz"

class database:
    token = getenv("DB_CONFIG")
    db_name = "cfc_bot"

class server:
    host = str(getenv("SERVER_HOST"))
    port = int(getenv("SERVER_PORT"))

class emoji:
    bot_ping = "<:bot_ping:1267199109027201147>"
    db_ping = "<:db_ping:1267199058913660929>"
    arrow = "<:new_arrow:1276772471252586639>"
    developer = "<:developer:1288934616480219226>"
    cache = "<:cache:1362040419957084373>"
    space = "<:empty_space:1362810768826961961>"
    back = "<:back:1367582929211101274>"
    angular_arrow = "<:angular_right:1367582937813483541>"
    invite = "<:link:1367582934953103413>"
    dot = "<:dot:1367588950146814093>"

    cog_admin = "<:admin:1262364323666202714>"
    cog_help = "<:help:1262364412497498164>"
    cog_tools = "<:tool:1254019437854588999>" 

class loging_channels:
    join = 1206246727116521504
    leave = 1206246727116521506
    mail = 1206246727116521505
    count = 1206246727116521507
    error_log = 1338082375761920053
    bot_log = 1369751023115177994

class color:
    no_color = 0x2c2c34

