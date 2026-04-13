from core import MyBot
from .misc import Misc

async def setup(bot: MyBot):
    await bot.add_cog(Misc(bot))