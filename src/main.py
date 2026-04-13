from core import MyBot
from api import app
import config
import uvicorn
from threading import Thread
from config import server

def run_api():
    uvicorn.run(app=app, host=server.host, port=server.port)

def boot():
    if config.bot.api:
        api_thread = Thread(target=run_api, daemon=True)
        api_thread.start()
        
    MyBot().boot()

if __name__ == "__main__":

    boot()