import discord
import asyncio
from discord.ext import commands

import config
from core.cog import Cog
from core.bot import MyBot
from .views import VoiceDropdownView


class Voice(Cog):
    """Temporary voice channel creation & management."""

    def __init__(self, bot: MyBot):
        self.bot = bot
        self.emoji = config.emoji.cog_voice
        # Register the persistent view so buttons/selects survive restarts
        self.bot.add_view(VoiceDropdownView(self.bot))


    @commands.group()
    async def voice(self, ctx: commands.Context):
        """Voice commands."""
        pass

    @voice.command()
    async def setup(self, ctx: commands.Context):
        """Set up Voice system for this server (server owner only)."""
        if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in self.bot.owner_ids:
            return await ctx.send(f"{ctx.author.mention} only the owner of the server can setup the bot!")

        def check(m):
            return m.author.id == ctx.author.id

        await ctx.send("**You have 60 seconds to answer each question!**")
        await ctx.send("**Enter the name of the category you wish to create the channels in: (e.g Voice Channels)**")

        try:
            category_msg = await self.bot.wait_for("message", check=check, timeout=60.0)
        except asyncio.TimeoutError:
            return await ctx.send("Took too long to answer!")

        new_cat = await ctx.guild.create_category_channel(category_msg.content)

        await ctx.send("**Enter the name of the voice channel: (e.g Join To Create)**")

        try:
            channel_msg = await self.bot.wait_for("message", check=check, timeout=60.0)
        except asyncio.TimeoutError:
            return await ctx.send("Took too long to answer!")

        try:
            channel = await ctx.guild.create_voice_channel(channel_msg.content, category=new_cat)

            await self.bot.db["voice_guilds"].update_one(
                {"guild_id": ctx.guild.id},
                {
                    "$set": {
                        "guild_id": ctx.guild.id,
                        "owner_id": ctx.author.id,
                        "voice_channel_id": channel.id,
                        "voice_category_id": new_cat.id,
                    }
                },
                upsert=True,
            )
            await ctx.send("**You are all setup and ready to go!**")
        except Exception:
            await ctx.send("You didn't enter the names properly.\nUse the setup command again!")

    @setup.error
    async def setup_error(self, ctx, error):
        self.bot.logger.error(f"[Voice] Setup error: {error}")

    @commands.command()
    async def setlimit(self, ctx: commands.Context, num: int):
        """Set the default channel limit for the server (server owner only)."""
        if ctx.author.id != ctx.guild.owner_id and ctx.author.id not in self.bot.owner_ids:
            return await ctx.send(f"{ctx.author.mention} only the owner of the server can setup the bot!")

        await self.bot.db["voice_guild_settings"].update_one(
            {"guild_id": ctx.guild.id},
            {
                "$set": {
                    "guild_id": ctx.guild.id,
                    "channel_name": f"{ctx.author.name}'s channel",
                    "channel_limit": num,
                }
            },
            upsert=True,
        )
        await ctx.send("You have changed the default channel limit for your server!")

    @voice.command()
    async def lock(self, ctx: commands.Context):
        """Lock your voice channel."""
        doc = await self.bot.db["voice_channels"].find_one({"user_id": ctx.author.id})
        if doc is None:
            return await ctx.send(f"{ctx.author.mention} You don't own a channel.")

        channel = self.bot.get_channel(doc["voice_id"])
        await channel.set_permissions(ctx.guild.default_role, connect=False)
        await ctx.send(f"{ctx.author.mention} Voice chat locked! 🔒")

    @voice.command()
    async def unlock(self, ctx: commands.Context):
        """Unlock your voice channel."""
        doc = await self.bot.db["voice_channels"].find_one({"user_id": ctx.author.id})
        if doc is None:
            return await ctx.send(f"{ctx.author.mention} You don't own a channel.")

        channel = self.bot.get_channel(doc["voice_id"])
        await channel.set_permissions(ctx.guild.default_role, connect=True)
        await ctx.send(f"{ctx.author.mention} Voice chat unlocked! 🔓")

    @voice.command(aliases=["allow"])
    async def permit(self, ctx: commands.Context, member: discord.Member):
        """Permit a user to join your voice channel."""
        doc = await self.bot.db["voice_channels"].find_one({"user_id": ctx.author.id})
        if doc is None:
            return await ctx.send(f"{ctx.author.mention} You don't own a channel.")

        channel = self.bot.get_channel(doc["voice_id"])
        await channel.set_permissions(member, connect=True)
        await ctx.send(f"{ctx.author.mention} You have permitted {member.name} to have access to the channel. ✅")

    @voice.command(aliases=["deny"])
    async def reject(self, ctx: commands.Context, member: discord.Member):
        """Reject a user from your voice channel."""
        doc = await self.bot.db["voice_channels"].find_one({"user_id": ctx.author.id})
        if doc is None:
            return await ctx.send(f"{ctx.author.mention} You don't own a channel.")

        channel = self.bot.get_channel(doc["voice_id"])

        # Kick them out if they're currently in the channel
        for m in channel.members:
            if m.id == member.id:
                guild_doc = await self.bot.db["voice_guilds"].find_one({"guild_id": ctx.guild.id})
                if guild_doc:
                    lobby = self.bot.get_channel(guild_doc["voice_channel_id"])
                    await member.move_to(lobby)
                break

        await channel.set_permissions(member, connect=False, read_messages=True)
        await ctx.send(f"{ctx.author.mention} You have rejected {member.name} from accessing the channel. ❌")

    @voice.command()
    async def limit(self, ctx: commands.Context, limit: int):
        """Set the user limit for your voice channel."""
        doc = await self.bot.db["voice_channels"].find_one({"user_id": ctx.author.id})
        if doc is None:
            return await ctx.send(f"{ctx.author.mention} You don't own a channel.")

        channel = self.bot.get_channel(doc["voice_id"])
        await channel.edit(user_limit=limit)
        await ctx.send(f"{ctx.author.mention} You have set the channel limit to be {limit}!")

        # Save preference
        await self.bot.db["voice_user_settings"].update_one(
            {"user_id": ctx.author.id},
            {
                "$set": {
                    "user_id": ctx.author.id,
                    "channel_limit": limit,
                },
                "$setOnInsert": {
                    "channel_name": f"{ctx.author.name}'s channel",
                },
            },
            upsert=True,
        )

    @voice.command()
    async def name(self, ctx: commands.Context, *, name: str):
        """Rename your voice channel."""
        doc = await self.bot.db["voice_channels"].find_one({"user_id": ctx.author.id})
        if doc is None:
            return await ctx.send(f"{ctx.author.mention} You don't own a channel.")

        channel = self.bot.get_channel(doc["voice_id"])
        await channel.edit(name=name)
        await ctx.send(f"{ctx.author.mention} You have changed the channel name to {name}!")

        # Save preference
        await self.bot.db["voice_user_settings"].update_one(
            {"user_id": ctx.author.id},
            {
                "$set": {
                    "user_id": ctx.author.id,
                    "channel_name": name,
                },
                "$setOnInsert": {
                    "channel_limit": 0,
                },
            },
            upsert=True,
        )

    @voice.command()
    async def claim(self, ctx: commands.Context):
        """Claim ownership of the voice channel if the owner has left."""
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f"{ctx.author.mention} you're not in a voice channel.")

        channel = ctx.author.voice.channel
        doc = await self.bot.db["voice_channels"].find_one({"voice_id": channel.id})

        if doc is None:
            return await ctx.send(f"{ctx.author.mention} You can't own that channel!")

        owner_id = doc["user_id"]
        if any(m.id == owner_id for m in channel.members):
            owner = ctx.guild.get_member(owner_id)
            return await ctx.send(
                f"{ctx.author.mention} This channel is already owned by {owner.mention}!"
            )

        await self.bot.db["voice_channels"].update_one(
            {"voice_id": channel.id},
            {"$set": {"user_id": ctx.author.id}},
        )
        await ctx.send(f"{ctx.author.mention} You are now the owner of the channel!")
