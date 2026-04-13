from discord.ext import commands
import discord
from datetime import timedelta
from typing import Optional

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="purge", description="Purge messages or delete N messages from a specific user.") 
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def purge(
    self,
    ctx: commands.Context,
    limit: int,
    user: Optional[discord.Member] = None
    ):
        """
        Usage:
        - purge 100            → deletes the last 100 messages
        - purge @user 5        → deletes the last 5 messages from that user
        """
        # Safety guards
        if limit < 1:
            return await ctx.send("Count must be at least 1.")
        if limit > 1000 and user is None:
            return await ctx.send("For bulk channel purge, count must be ≤ 1000.")

        # Defer if slash command
        if ctx.interaction:
            await ctx.interaction.response.defer(ephemeral=True)

        try:
            if user is None:
                # Simple bulk purge: delete up to `count` recent messages (any author)
                deleted = await ctx.channel.purge(limit=limit)
                confirm = await ctx.send(f"Deleted {len(deleted)} message(s).")
                await confirm.delete(delay=5)
                return

            # Delete up to `count` messages from `target`
            cutoff = discord.utils.utcnow() - timedelta(days=14)  # bulk delete cannot include messages older than 14 days
            to_delete: list[discord.Message] = []

            # Scan recent history to collect up to `count` messages from the target
            async for msg in ctx.channel.history(limit=2000):  # adjust window as needed
                if msg.author == user and msg.created_at > cutoff:
                    to_delete.append(msg)
                    if len(to_delete) >= limit:
                        break

            if not to_delete:
                confirm = await ctx.send(f"No deletable recent messages found from {user.mention}.")
                await confirm.delete(delay=5)
                return

            # Bulk delete in chunks of up to 100; single message via .delete()
            deleted_total = 0
            i = 0
            while i < len(to_delete):
                chunk = to_delete[i:i+100]
                if len(chunk) >= 2:
                    await ctx.channel.delete_messages(chunk)
                    deleted_total += len(chunk)
                else:
                    await chunk[0].delete()
                    deleted_total += 1
                i += 100

            if ctx.interaction:
                await ctx.interaction.followup.send(f"Deleted {deleted_total} messages.", ephemeral=True)
            else:
                confirm = await ctx.send(f"Deleted {deleted_total} messages.")
                await confirm.delete(delay=5)

        except discord.Forbidden:
            await ctx.send("I don’t have permission to manage messages here.")
        except discord.HTTPException as e:
            await ctx.send(f"An error occurred: {e}")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
    