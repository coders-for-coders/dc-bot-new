from os import getenv
from dotenv import load_dotenv

load_dotenv()

class bot:
    token = getenv("DISCORD_TOKEN")
    default_prefix = "t."
    api = True
    owner_ids = {int(x.strip()) for x in getenv("OWNER_ID", "").split(",") if x.strip()}
    default_status = "CFC bot"
    cogs = [
        "tools",
        "voice",
        "jishaku",
        "dev",
        "events",
        "help"
        # "games"
    ]
    
    support_invite = "https://discord.gg/dn2dpgCbXP"
    invite_link = ""
    vote_link = ""
    website = "https://codersforcoders.xyz"

class help:
    ignored_cogs = ["Dev", "Events", "Jishaku", "Error", "VoiceEvents"]

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
    cog_games = "<:Minecraft:1277279364316139601>" 
    cog_voice = "<:voice:1494090963256086649>"
    cog_dev = "" 
    cog_help = "<:help:1262364412497498164>"

class loging_channels:
    join = 1206246727116521504
    leave = 1206246727116521506
    mail = 1206246727116521505
    count = 1206246727116521507
    error_log = 1338082375761920053
    bot_log = 1369751023115177994

class color:
    no_color = 0x2c2c34