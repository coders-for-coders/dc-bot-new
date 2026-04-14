import discord
import asyncio

from core.cog import Cog
from core.bot import MyBot
from .views import VoiceDropdownView

class VoiceEvents(Cog):
    """Temporary voice channel events."""

    def __init__(self, bot: MyBot):
        self.bot = bot

    @Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        guild_id = member.guild.id

        guild_doc = await self.bot.db["voice_guilds"].find_one({"guild_id": guild_id})
        if guild_doc is None:
            return

        voice_channel_id = guild_doc["voice_channel_id"]

        try:
            if after.channel is None or after.channel.id != voice_channel_id:
                return

            # Check cooldown — user already has a temp channel
            existing = await self.bot.db["voice_channels"].find_one({"user_id": member.id})
            if existing:
                try:
                    await member.send(
                        "Creating channels too quickly — you've been put on a 15 second cooldown!"
                    )
                except discord.Forbidden:
                    pass
                await asyncio.sleep(15)

            # Fetch guild settings
            category_id = guild_doc["voice_category_id"]
            category = self.bot.get_channel(category_id)

            user_settings = await self.bot.db["voice_user_settings"].find_one({"user_id": member.id})
            guild_settings = await self.bot.db["voice_guild_settings"].find_one({"guild_id": guild_id})

            if user_settings is None:
                name = f"{member.name}'s channel"
                limit = guild_settings["channel_limit"] if guild_settings else 0
            else:
                name = user_settings.get("channel_name", f"{member.name}'s channel")
                user_limit = user_settings.get("channel_limit", 0)
                if guild_settings and user_limit == 0:
                    limit = guild_settings["channel_limit"]
                else:
                    limit = user_limit

            # Create the temporary voice channel
            channel = await member.guild.create_voice_channel(name, category=category)
            await member.move_to(channel)
            await channel.set_permissions(self.bot.user, connect=True, read_messages=True)
            await channel.set_permissions(member, connect=True, read_messages=True)
            await channel.edit(name=name, user_limit=limit)

            # Track ownership
            await self.bot.db["voice_channels"].insert_one(
                {"user_id": member.id, "voice_id": channel.id}
            )

            # Send the control panel embed
            embed = discord.Embed(
                title="⚙️ Welcome to your own temporary voice channel",
                description=(
                    "Control your channel using the menus below.\n\n"
                    "**Channel Settings**\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "Modify your channel settings using the menu below.\n\n"
                    "**Channel Permissions**\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "Modify your channel permissions using the menu below.\n\n"
                    "**Gold options require voting**"
                ),
                color=0x5865F2,
            )
            embed.set_footer(
                text="Manage your channel permissions and settings.",
                icon_url=self.bot.user.display_avatar.url,
            )

            try:
                await channel.send(embed=embed, view=VoiceDropdownView(self.bot))
            except Exception as e:
                self.bot.logger.error(f"[Voice] Error sending interface: {e}")

            # Wait for the channel to empty, then clean up
            def check(a, b, c):
                return len(channel.members) == 0

            await self.bot.wait_for("voice_state_update", check=check)
            await channel.delete()
            await asyncio.sleep(3)
            await self.bot.db["voice_channels"].delete_one({"user_id": member.id})

        except Exception:
            pass
