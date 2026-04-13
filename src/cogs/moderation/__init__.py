from core import MyBot
from .moderation import Moderation

async def setup(bot: MyBot):
    await bot.add_cog(Moderation(bot))