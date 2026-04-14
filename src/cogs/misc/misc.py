from discord.ext import commands
import random

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='8ball', aliases=['wisdom'])
    async def ball(self, ctx, *, question):
        responseArr = [
                "It is certain.",
                "It is decidedly so.",
                "Without a doubt.",
                "Yes - definitely.",
                "You may rely on it.",
                "As I see it, yes.",
                "Most likely.",
                "Outlook good.",
                "Yes.",
                "Signs point to yes.",
                "Reply hazy, try again.",
                "Ask again later.",
                "Better not tell you now.",
                "Cannot predict now.",
                "Concentrate and ask again.",
                "Don't count on it.",
                "My reply is no.",
                "My sources say no.",
                "Outlook not so good.",
                "Very doubtful."]
        response = random.choice(responseArr)
        await ctx.message.reply(response)

async def setup(bot):
    await bot.add_cog(Misc(bot))