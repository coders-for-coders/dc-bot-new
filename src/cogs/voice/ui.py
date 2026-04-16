import discord


class RenameModal(discord.ui.Modal, title="Rename Your Channel"):
    name = discord.ui.TextInput(
        label="New Channel Name",
        placeholder="Enter name...",
        min_length=2,
        max_length=50,
    )

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await interaction.user.voice.channel.edit(name=self.name.value)
        await interaction.followup.send(
            f"Channel renamed to **{self.name.value}**!", ephemeral=True
        )


class LimitModal(discord.ui.Modal, title="Set User Limit"):
    limit = discord.ui.TextInput(
        label="User Limit (0-99)",
        placeholder="0 for no limit",
        min_length=1,
        max_length=2,
    )

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            val = int(self.limit.value)
            await interaction.user.voice.channel.edit(user_limit=val)
            await interaction.followup.send(
                f"User limit set to **{val}**!", ephemeral=True
            )
        except ValueError:
            await interaction.followup.send("Invalid limit!", ephemeral=True)


class StatusModal(discord.ui.Modal, title="Set Channel Status"):
    status = discord.ui.TextInput(
        label="What are you doing?",
        placeholder="e.g. Playing Ranked",
        min_length=2,
        max_length=50,
    )

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await interaction.user.voice.channel.edit(name=f"💬 {self.status.value}")
        await interaction.followup.send(
            f"Channel status set to **{self.status.value}**!", ephemeral=True
        )


class MemberModal(discord.ui.Modal):
    user_input = discord.ui.TextInput(
        label="User ID or @Mention",
        placeholder="Paste the user ID or tag them here...",
        min_length=2,
    )

    def __init__(self, bot, action: str):
        super().__init__(title=f"{action} User")
        self.bot = bot
        self.action = action

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        # Resolve user from input
        input_str = self.user_input.value.replace("<@", "").replace(">", "").replace("!", "")
        try:
            user_id = int(input_str)
            user = await self.bot.fetch_user(user_id)
        except (ValueError, discord.NotFound):
            return await interaction.followup.send(
                "Invalid User ID or Mention!", ephemeral=True
            )

        channel = interaction.user.voice.channel

        if self.action == "Permit":
            await channel.set_permissions(user, connect=True)
            await interaction.followup.send(
                f"**{user.name}** is now permitted to join! ✅", ephemeral=True
            )
        elif self.action == "Reject":
            await channel.set_permissions(user, connect=False)
            member = interaction.guild.get_member(user.id)
            if member and member.voice and member.voice.channel and member.voice.channel.id == channel.id:
                await member.move_to(None)
            await interaction.followup.send(
                f"**{user.name}** has been rejected! ❌", ephemeral=True
            )
        elif self.action == "Transfer":
            await self.bot.db["voice_channels"].update_one(
                {"voice_id": channel.id},
                {"$set": {"user_id": user.id}},
            )
            await interaction.followup.send(
                f"Ownership of the channel transferred to **{user.mention}**! 👑",
                ephemeral=True,
            )


class BitrateModal(discord.ui.Modal, title="Set Channel Bitrate"):
    bitrate = discord.ui.TextInput(
        label="Bitrate (8-96)",
        placeholder="e.g. 64",
        min_length=1,
        max_length=2,
    )

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        try:
            val = int(self.bitrate.value) * 1000
            await interaction.user.voice.channel.edit(bitrate=val)
            await interaction.response.send_message(
                f"Bitrate set to **{self.bitrate.value}kbps**!", ephemeral=True
            )
        except (ValueError, discord.HTTPException):
            await interaction.response.send_message(
                "Invalid bitrate!", ephemeral=True
            )


class RegionModal(discord.ui.Modal, title="Set Channel Region"):
    region = discord.ui.TextInput(
        label="Region (e.g. us-central, rotterdam)",
        placeholder="Enter region name...",
        min_length=2,
    )

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await interaction.user.voice.channel.edit(rtc_region=self.region.value)
            await interaction.response.send_message(
                f"Region set to **{self.region.value}**!", ephemeral=True
            )
        except discord.HTTPException:
            await interaction.response.send_message(
                "Invalid region!", ephemeral=True
            )

class SetupModal(discord.ui.Modal, title="Voice Setup"):
    category_name = discord.ui.TextInput(
        label="Category Name",
        placeholder="e.g Voice Channels",
        min_length=1,
        max_length=100,
    )
    channel_name = discord.ui.TextInput(
        label="Voice Channel Name",
        placeholder="e.g Join To Create",
        min_length=1,
        max_length=100,
    )

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        guild = interaction.guild
        try:
            new_cat = await guild.create_category_channel(self.category_name.value)
            channel = await guild.create_voice_channel(self.channel_name.value, category=new_cat)

            await self.bot.db["voice_guilds"].update_one(
                {"guild_id": guild.id},
                {
                    "$set": {
                        "guild_id": guild.id,
                        "voice_channel_id": channel.id,
                        "voice_category_id": new_cat.id,
                    }
                },
                upsert=True,
            )
            await interaction.followup.send("**You are all setup and ready to go!**")
        except Exception:
            await interaction.followup.send("You didn't enter the names properly.\nUse the setup command again!")
