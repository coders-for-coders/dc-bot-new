from core import MyBot
from .fun import Fun

async def setup(bot: MyBot):
    await bot.add_cog(Fun(bot))