import random
from discord.ext import commands

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="compliment", description="Get a random compliment")
    async def compliment(self, ctx: commands.Context, member: commands.MemberConverter = None):
        compliments = [
            "You're awesome!", "You light up the room!",
            "You have great energy!", "You're a true friend!"
        ]
        target = member.mention if member else ctx.author.mention
        await ctx.send(f"💖 {target}, {random.choice(compliments)}")

    @commands.command(name="roast", description="Playfully roast someone")
    async def roast(self, ctx: commands.Context, member: commands.MemberConverter):
        roasts = [
            "You bring WiFi dead zones wherever you go.",
            "You have the personality of a dial tone.",
            "You're proof evolution can go in reverse."
        ]
        await ctx.send(f"🔥 {member.mention}, {random.choice(roasts)}")

async def setup(bot):
    await bot.add_cog(Fun(bot))