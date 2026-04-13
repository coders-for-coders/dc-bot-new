from fastapi import FastAPI
from discord.ext import commands

app = FastAPI()

bot: commands.Bot | None = None

def set_bot_instance(bot_instance: commands.Bot):
    global bot
    bot = bot_instance


@app.get("/")
async def root():
    return {
        "message": "Hello World",
        "ping": round(bot.latency * 1000, 2) if bot else None
        }