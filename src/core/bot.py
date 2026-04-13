import discord
from discord.ext import commands
import config
import asyncio
import time
from typing import Callable, Coroutine, List
from motor.motor_asyncio import AsyncIOMotorClient
import logging
from api import set_bot_instance


startup_task: List[Callable[["MyBot"], Coroutine]] = []
class MyBot(commands.Bot):
    """Custom class inherited from commands.Bot"""

    def __init__(self, **kwargs):
        super().__init__(
            command_prefix = get_prefix,
            intents = discord.Intents.all(),
            owner_ids = config.bot.owner_ids,
            case_insensitive = True,
            **kwargs
            )
        
        self.uptime = None
        self.setup_logger()
        self.help_command = None

        self.prefix_cache = {}
        self.ping_cache = {"ping":"pong"}

        self.np_cache = {}


    async def on_command_error(self, ctx: commands.Context, error):
            if isinstance(error, commands.CommandNotFound):
                return  # Return because we don't want to show an error for every command not found
            elif isinstance(error, commands.CommandOnCooldown):
                message = f"This command is on cooldown. Please try again after {round(error.retry_after, 1)} seconds."
            elif isinstance(error, commands.MissingPermissions):
                message = "You are missing the required permissions to run this command!"
            elif isinstance(error, commands.UserInputError):
                message = message = str(error) or "Something about your input was wrong, please check your input and try again!"
            else:
                message = "Oh no! Something went wrong while running the command!"
                print(error)

            await ctx.send(message, delete_after=10)


    def boot(self):
        try:
            self.logger.info("Bot is booting....")
            super().run(token=config.bot.token)

        except Exception as e:
            self.logger.error("Bot shutting down....")
            self.logger.error(f"An error occurred: {e}\n")

    def setup_logger(self):
        self.logger = logging.getLogger(" ")
        self.logger.setLevel(logging.INFO)
        
        dt_fmt = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(
            "{asctime} {levelname:<8} {name} {message}", dt_fmt, style="{"
        )

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        for logger_name in ('asyncio', 'wavelink', 'discord.voice_state'):
            logging.getLogger(logger_name).setLevel(logging.CRITICAL)


    async def load_cache(self):

        # Load prefix cache
        data = await self.db["prefix"].find({}).to_list()
        for entry in data:
            self.prefix_cache[entry["guild_id"]] = entry["prefix"]
        self.logger.info("Loaded prefix cache")


        # load np cache
        data = await self.db["np"].find({}).to_list()
        for entry in data:
            self.np_cache[entry["uid"]] = "np"



    async def setup_hook(self):
        self.uptime = time.time()
        await asyncio.gather(*(task(self) for task in startup_task))
        await self.load_cache()
        set_bot_instance(self)

    global get_prefix
    async def get_prefix(self, message: discord.Message):

        prefixes = []

        np_prefix = self.np_cache.get(message.author.id)
        if message.guild is None:
            prefixes.append(config.bot.default_prefix)
            if np_prefix:
                prefixes.append("")
        else:
            guild_prefix = self.prefix_cache.get(message.guild.id)
            if guild_prefix:
                prefixes.append(guild_prefix)
            else:
                prefixes.append(config.bot.default_prefix)
            if np_prefix:
                prefixes.append("")

        return commands.when_mentioned_or(*prefixes)(self, message)


    
    @startup_task.append
    async def setup_db(self):
        try:
            self.db = AsyncIOMotorClient(config.database.token)[config.database.db_name]
            self.logger.info("Connected to database")

        except Exception as e:
            self.logger.error("Failed to load database")
            self.logger.error(e)


    @startup_task.append
    async def setup_cogs(self):
        for cog in config.bot.cogs:
            try:
                if cog == "jishaku":
                    await self.load_extension(cog)
                else:
                    await self.load_extension(f"cogs.{cog}")
                self.logger.info(f"Loaded {cog}")
            except Exception as e:
                self.logger.error(f"Failed to load: {cog}")
                self.logger.error(e)
        self.logger.info("Loaded all cogs")

