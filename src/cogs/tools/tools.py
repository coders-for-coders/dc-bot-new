import discord
from discord.ext import commands
import config
from core.cog import Cog
from main import MyBot
import time


class Tools (Cog):
    def __init__(self, bot: MyBot):
        self.bot=bot
        self.emoji = config.emoji.cog_tools


    #hybrid command for ping
    @commands.hybrid_command(with_app_command=True, name="ping",description="Shows the latency", aliases=["latency"])
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.user)
    async def ping(self, ctx:commands.Context):

        # bot ping
        bot_ping = int(self.bot.latency*1000)

        # database ping
        tm = time.time()
        await self.bot.db["homie"]["ping"].find_one({"ping":"pong"})
        db_ping = int((time.time()-tm)*1000)


        #cache ping
        tm = time.time()
        self.bot.ping_cache.get("ping")
        cache_ping = round((time.time()-tm)*1000, 3)

        embed = discord.Embed()
        embed.description = f"{config.emoji.bot_ping} Bot ping: `{bot_ping} ms`\n \n{config.emoji.db_ping} Database ping: `{db_ping} ms` \n \n{config.emoji.cache} Cache ping: `{cache_ping} ms`"
        embed.color=config.color.no_color
        
        embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar.url)
        await ctx.send(embed=embed)

