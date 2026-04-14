from core import MyBot
from .voice import Voice
from .events import VoiceEvents

async def setup(bot: MyBot):
    await bot.add_cog(Voice(bot))
    await bot.add_cog(VoiceEvents(bot))
