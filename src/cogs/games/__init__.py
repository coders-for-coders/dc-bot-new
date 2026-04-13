from core import MyBot
from .games import Games

async def setup(bot: MyBot):
    await bot.add_cog(Games(bot))