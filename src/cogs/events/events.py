import discord
from core.cog import Cog
from core.bot import MyBot
import config
import time

class Events(Cog):
    def __init__(self, bot: MyBot):
        self.bot = bot
        self.cooldowns = {}
        self.check_nodes.start()
        self.leave_tasks = {}


    @Cog.listener("on_ready")
    async def on_ready_main(self):
        #general
        self.bot.logger.info(f"Bot is ready as {self.bot.user}")
        status = await self.bot.db["status"].find_one({"status": {"$exists": True}})
        await self.bot.change_presence(activity=discord.CustomActivity(name=status["status"] if status else config.bot.default_status))

        #restart
        data = await self.bot.db["restart"].find_one({"restart": "restart"})
        if data:
            channel = self.bot.get_channel(data["channel_id"])
            message = await channel.fetch_message(data["message_id"])
            await message.reply(f"Successfully restarted in `{round(time.time() - data['time'], 1)}` seconds")
            await self.bot.db["restart"].delete_one({"restart": "restart"})
