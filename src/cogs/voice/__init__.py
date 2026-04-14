from core import MyBot
from .voice import Voice

async def setup(bot: MyBot):
    await bot.add_cog(Voice(bot))
