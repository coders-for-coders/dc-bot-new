import discord
from core.bot import MyBot
import config

from .ui import (
    RenameModal,
    LimitModal,
    StatusModal,
    MemberModal,
    BitrateModal,
    RegionModal,
)


class ChannelSettingsSelect(discord.ui.Select):
    """Dropdown for channel settings: Name, Limit, Status, Game, LFM, Bitrate, Region, Text, NSFW, Claim."""

    def __init__(self, bot: MyBot):
        self.bot = bot
        options = [
            discord.SelectOption(label="Name", description="Change the channel name", emoji="📝"),
            discord.SelectOption(label="Limit", description="Change the channel limit", emoji="👥"),
            discord.SelectOption(label="Status", description="Change the channel status", emoji="💬"),
            discord.SelectOption(label="Game", description="Change name to the game you're playing", emoji="🎮"),
            discord.SelectOption(label="LFM", description="Post a message to the LFM channel", emoji="👤"),
            discord.SelectOption(label="Bitrate", description="Change the channel bitrate", emoji="📶"),
            discord.SelectOption(label="Region", description="Change the channel voice region", emoji="🌐"),
            discord.SelectOption(label="Text", description="Create a temporary text channel", emoji="💬"),
            discord.SelectOption(label="NSFW", description="Set your temporary channel to NSFW", emoji="⚠️"),
            discord.SelectOption(label="Claim", description="Claim ownership of the channel", emoji="👑"),
        ]
        super().__init__(
            placeholder="Change channel settings",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="voice_settings_select",
        )

    async def callback(self, interaction: discord.Interaction):
        if not await self.view.check_owner(interaction):
            return

        val = self.values[0]

        if val == "Name":
            await interaction.response.send_modal(RenameModal(self.bot))

        elif val == "Limit":
            await interaction.response.send_modal(LimitModal(self.bot))

        elif val == "NSFW":
            await interaction.response.defer(ephemeral=True)
            channel = interaction.user.voice.channel
            await channel.edit(nsfw=not channel.nsfw)
            state = "Enabled" if channel.nsfw else "Disabled"
            await interaction.followup.send(f"NSFW is now **{state}**!", ephemeral=True)

        elif val == "Bitrate":
            await interaction.response.send_modal(BitrateModal(self.bot))

        elif val == "Region":
            await interaction.response.send_modal(RegionModal(self.bot))

        elif val == "Claim":
            await interaction.response.defer(ephemeral=True)
            await self.view.claim_logic(interaction)

        elif val == "Status":
            await interaction.response.send_modal(StatusModal(self.bot))

        elif val == "LFM":
            await interaction.response.defer(ephemeral=True)
            await self._lfm_broadcast(interaction)

        elif val == "Game":
            await interaction.response.defer(ephemeral=True)
            activity = interaction.user.activity
            if activity:
                await interaction.user.voice.channel.edit(name=f"🎮 {activity.name}")
                await interaction.followup.send(
                    f"Channel renamed to **🎮 {activity.name}**!", ephemeral=True
                )
            else:
                await interaction.followup.send(
                    "You are not playing any game!", ephemeral=True
                )

        elif val == "Text":
            await interaction.response.defer(ephemeral=True)
            guild = interaction.guild
            member = interaction.user
            category = interaction.user.voice.channel.category
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                member: discord.PermissionOverwrite(read_messages=True),
                guild.me: discord.PermissionOverwrite(read_messages=True),
            }
            text_channel = await guild.create_text_channel(
                name=f"chat-{member.name}", category=category, overwrites=overwrites
            )
            await interaction.followup.send(
                f"Temporary text channel created: {text_channel.mention}", ephemeral=True
            )

        else:
            await interaction.response.send_message(
                f"You selected **{val}** (Coming soon!)", ephemeral=True
            )

    async def _lfm_broadcast(self, interaction: discord.Interaction):
        lfm_channel = discord.utils.get(interaction.guild.text_channels, name="lfm")
        if not lfm_channel:
            return await interaction.followup.send(
                "Please create an **#lfm** channel first!", ephemeral=True
            )

        invite = await interaction.user.voice.channel.create_invite(max_age=3600)
        embed = discord.Embed(
            title="🎮 Looking for More!",
            description=f"{interaction.user.mention} is looking for players to join their voice channel!",
            color=discord.Color.green(),
        )
        embed.add_field(name="Join Now", value=f"[Click to Join Voice]({invite})")
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await lfm_channel.send(embed=embed)
        await interaction.followup.send("Broadcasted your LFM request! 📢", ephemeral=True)


class ChannelPermissionsSelect(discord.ui.Select):
    """Dropdown for channel permissions: Lock, Unlock, Permit, Reject, Invite, Ghost, Unghost, Transfer."""

    def __init__(self, bot):
        self.bot = bot
        options = [
            discord.SelectOption(label="Lock", description="Lock the channel", emoji="🔒"),
            discord.SelectOption(label="Unlock", description="Unlock the channel", emoji="🔓"),
            discord.SelectOption(label="Permit", description="Permit users/roles to access the channel", emoji="👤"),
            discord.SelectOption(label="Reject", description="Reject/kick users/roles from the channel", emoji="👤"),
            discord.SelectOption(label="Invite", description="Invite a user to access the channel", emoji="👤"),
            discord.SelectOption(label="Ghost", description="Make your channel invisible", emoji="👻"),
            discord.SelectOption(label="Unghost", description="Make your channel visible", emoji="👁️"),
            discord.SelectOption(label="Transfer", description="Transfer ownership to another user", emoji="⭐"),
        ]
        super().__init__(
            placeholder="Change channel permissions",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="voice_permissions_select",
        )

    async def callback(self, interaction: discord.Interaction):
        if not await self.view.check_owner(interaction):
            return

        val = self.values[0]

        if val == "Lock":
            await interaction.response.defer(ephemeral=True)
            await interaction.user.voice.channel.set_permissions(
                interaction.guild.default_role, connect=False
            )
            await interaction.followup.send("Channel **Locked**! 🔒", ephemeral=True)

        elif val == "Unlock":
            await interaction.response.defer(ephemeral=True)
            await interaction.user.voice.channel.set_permissions(
                interaction.guild.default_role, connect=True
            )
            await interaction.followup.send("Channel **Unlocked**! 🔓", ephemeral=True)

        elif val == "Ghost":
            await interaction.response.defer(ephemeral=True)
            await interaction.user.voice.channel.set_permissions(
                interaction.guild.default_role, view_channel=False
            )
            await interaction.followup.send("Channel **Hidden** (Ghost)! 👻", ephemeral=True)

        elif val == "Unghost":
            await interaction.response.defer(ephemeral=True)
            await interaction.user.voice.channel.set_permissions(
                interaction.guild.default_role, view_channel=True
            )
            await interaction.followup.send("Channel is now **Visible**! 👁️", ephemeral=True)

        elif val == "Invite":
            await interaction.response.defer(ephemeral=True)
            invite = await interaction.user.voice.channel.create_invite(max_age=3600)
            await interaction.followup.send(f"Invite created: {invite}", ephemeral=True)

        elif val == "Permit":
            await interaction.response.send_modal(MemberModal(self.bot, "Permit"))

        elif val == "Reject":
            await interaction.response.send_modal(MemberModal(self.bot, "Reject"))

        elif val == "Transfer":
            await interaction.response.send_modal(MemberModal(self.bot, "Transfer"))

        else:
            await interaction.response.send_message(
                f"You selected **{val}** (Coming soon!)", ephemeral=True
            )


class VoiceDropdownView(discord.ui.View):
    """Persistent view with settings & permissions dropdowns + utility buttons."""

    def __init__(self, bot: MyBot):
        super().__init__(timeout=None)
        self.bot = bot
        self.add_item(ChannelSettingsSelect(self.bot))
        self.add_item(ChannelPermissionsSelect(self.bot))
        self.add_item(
            discord.ui.Button(
                label="Dashboard",
                style=discord.ButtonStyle.secondary,
                emoji="🔗",
                url=config.bot.website,
            )
        )

    @discord.ui.button(
        label="Load Settings",
        style=discord.ButtonStyle.primary,
        emoji="⚙️",
        custom_id="voice_load",
    )
    async def load_settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("Loading your saved settings...", ephemeral=True)

    async def check_owner(self, interaction: discord.Interaction) -> bool:
        """Verify the interacting user owns the voice channel they're in."""
        if not interaction.user.voice or not interaction.user.voice.channel:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "You are not in a voice channel!", ephemeral=True
                )
            else:
                await interaction.followup.send(
                    "You are not in a voice channel!", ephemeral=True
                )
            return False

        doc = await self.bot.db["voice_channels"].find_one(
            {"voice_id": interaction.user.voice.channel.id}
        )

        if doc and doc["user_id"] == interaction.user.id:
            return True

        if not interaction.response.is_done():
            await interaction.response.send_message(
                "You are not the owner of this channel!", ephemeral=True
            )
        else:
            await interaction.followup.send(
                "You are not the owner of this channel!", ephemeral=True
            )
        return False

    async def claim_logic(self, interaction: discord.Interaction):
        """Allow a user to claim an abandoned channel."""
        channel = interaction.user.voice.channel
        doc = await self.bot.db["voice_channels"].find_one({"voice_id": channel.id})
        if doc:
            owner_id = doc["user_id"]
            if not any(m.id == owner_id for m in channel.members):
                await self.bot.db["voice_channels"].update_one(
                    {"voice_id": channel.id},
                    {"$set": {"user_id": interaction.user.id}},
                )
                await interaction.followup.send(
                    "You are now the **Owner**! 👑", ephemeral=True
                )
            else:
                await interaction.followup.send(
                    "The owner is still here!", ephemeral=True
                )

class SetupView(discord.ui.View):
    def __init__(self, bot: MyBot):
        super().__init__(timeout=60)
        self.bot = bot

    @discord.ui.button(label="Start Setup", style=discord.ButtonStyle.primary)
    async def start_setup(self, interaction: discord.Interaction, button: discord.ui.Button):
        from .ui import SetupModal
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Only administrators cansetup the bot!", ephemeral=True)
        await interaction.response.send_modal(SetupModal(self.bot))
