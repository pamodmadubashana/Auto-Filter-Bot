import os
import time
import asyncio
import uvloop

from pyrogram import types
from pyrogram import Client 
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from aiohttp import web
from typing import Union, Optional, AsyncGenerator

from web import web_app
from utils import temp, get_readable_time
from info import LOG_CHANNEL, API_ID, API_HASH, BOT_TOKEN, PORT, BIN_CHANNEL, ADMINS, DATABASE_URL  

from database.users_chats_db import db
from database.ia_filterdb import Media
from pymongo.server_api import ServerApi
from pymongo.mongo_client import MongoClient

uvloop.install()
def clear_terminal():
    if os.name == 'nt':
        os.system('cls')
    else: 
        os.system('clear')

class Bot(Client):
    def __init__(self):
        self._bot = Client(
            name='bot',
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins={"root": "plugins"}
        )
    async def create_user_clients(self):
        self._user = Client(
            name='user',
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=self.SESSION,
            plugins={"root": "user"}
        )
    async def start(self):
        temp.START_TIME = time.time()
        b_users, b_chats = await db.get_banned()
        self.SESSION = await db.get_user_session()
        if self.SESSION:
            await self.create_user_clients()
        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats
        client = MongoClient(DATABASE_URL, server_api=ServerApi('1'))
        try:
            client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print("Something Went Wrong While Connecting To Database!", e)
            exit()
        await self._bot.start()
        if os.path.exists('restart.txt'):
            with open("restart.txt") as file:
                chat_id, msg_id = map(int, file)
            try:
                await self._bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text='Restarted Successfully!')
            except:
                pass
            os.remove('restart.txt')
        temp.BOT = self._bot
        await Media.ensure_indexes()
        me = await self._bot.get_me()
        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        username = '@' + me.username
        print(f"{me.first_name} - {username} is started now 🤗")
        app = web.AppRunner(web_app)
        await app.setup()
        await web.TCPSite(app, "0.0.0.0", PORT).start()
        try:
            await self._bot.send_message(chat_id=LOG_CHANNEL, text=f"<b>{me.mention} Restarted! 🤖</b>")
        except:
            print("Error - Make sure bot admin in LOG_CHANNEL, exiting now")
            exit()
        if hasattr(self, '_user') and self._user:
            try:
                await self._user.start()
                self._user_data = await self._user.get_me()
                self.u_name = self._user_data.first_name
                self.u_username = f"@{self._user_data.username}" if self._user_data.username else ''
                print(f"{self.u_name} - {self.u_username} is started now 🤗")
            except Exception as e:
                await self._bot.send_message(LOG_CHANNEL,text=f"Error while validating user session: {e}")
        try:
            m = await self._bot.send_message(chat_id=BIN_CHANNEL, text="Test")
            await m.delete()
        except:
            print("Error - Make sure bot admin in BIN_CHANNEL, exiting now")
            exit()
        for admin in ADMINS:
            await self._bot.send_message(chat_id=admin, text="<b>✅ ʙᴏᴛ ʀᴇsᴛᴀʀᴛᴇᴅ</b>")

    async def stop(self, *args):
        await self._bot.stop()
        if hasattr(self, '_user') and self._user:await self._user.stop()
        clear_terminal()
        print("Bot Stopped! Bye...")

    async def iter_messages(self: Client, chat_id: Union[int, str], limit: int, offset: int = 0) -> Optional[AsyncGenerator["types.Message", None]]:
        current = offset
        while True:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_messages(chat_id, list(range(current, current+new_diff+1)))
            for message in messages:
                yield message
                current += 1

app = Bot()
try:
    app.run()
except FloodWait as vp:
    time = get_readable_time(vp.value)
    print(f"Flood Wait Occured, Sleeping For {time}")
    asyncio.sleep(vp.value)
    print("Now Ready For Deploying !")
    app.run()
