from .dev import Dev
from core.bot import MyBot

async def setup(bot: MyBot):
    await bot.add_cog(Dev(bot))