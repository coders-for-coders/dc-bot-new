import discord
from discord.ext import commands
from core.cog import Cog
from core.bot import MyBot
import time
import subprocess
from discord.ui import View, Button
import json


class Dev(Cog):
    def __init__(self, bot: MyBot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.is_owner()
    async def restart(self, ctx: commands.Context):

        with open("pm2.json", "r") as f:
            data = json.load(f)
            app_name = data["apps"][0]["name"]

        yes_btn = Button(
            label="Yes",
            style=discord.ButtonStyle.green
        )
        no_btn = Button(
            label="No",
            style=discord.ButtonStyle.red
        )
        view = View(timeout=None)
        view.add_item(yes_btn)
        view.add_item(no_btn)

        msg: discord.Message = await ctx.send("> Confirm restart?", view=view, delete_after=60)
        
        async def yes_callback(interaction: discord.Interaction):
            if interaction.user.id != ctx.author.id:
                return await interaction.response.send_message("You can't use this button.", ephemeral=True)

            await interaction.response.defer()
            await msg.delete()
            await ctx.send(f"Restarting the bot using `pm2 restart {app_name}`...")
            await self.bot.db["restart"].insert_one({
                "restart": "restart",
                "time": time.time(),
                "channel_id": ctx.channel.id,
                "message_id" : ctx.message.id
            })

            try:
                subprocess.run(["pm2", "restart", app_name], capture_output=True, text=True)
            except Exception as e:
                await ctx.send(f"Exception occurred: `{str(e)}`")

        async def no_callback(interaction: discord.Interaction):
            if interaction.user.id != ctx.author.id:
                return await interaction.response.send_message("You can't use this button.", ephemeral=True)
            
            await interaction.response.defer()
            await msg.delete()
            await ctx.send("Restart cancelled.", delete_after=5)

        yes_btn.callback = yes_callback
        no_btn.callback = no_callback