from pyrogram import Client , filters
from pyrogram.types import Message , CallbackQuery
from pyrogram.errors import PhoneNumberInvalid, PhoneCodeInvalid, PhoneCodeExpired, SessionPasswordNeeded, PasswordHashInvalid
from os import environ
from database.users_chats_db import db
API_ID = environ.get('API_ID', '28484794')
API_HASH = environ.get('API_HASH', '8786a3f10dfe603e5e3517f5d6dbfebc')
BOT_TOKEN = environ.get('BOT_TOKEN', '7236782282:AAFuG6uDxUMNnmUJDMtqTcGGAg38tlWXGqQ')
OWNER_ID = 5040666523


async def log_in(client: Client, message):
    user_client = Client(name="user", api_id=API_ID, api_hash=API_HASH, in_memory=True)
    async def get_number(text = "Give me the phone number"):
        return (await client.ask(chat_id=OWNER_ID, text=text, filters=filters.text)).text
    
    async def send_code(phone_number):
        status = True
        while status:
            try:
                code = await user_client.send_code(phone_number)
                status = False
            except PhoneNumberInvalid:
                await get_number('This number is invalid , Try Again')
        return code
    
    async def get_code(text="» ᴩʟᴇᴀsᴇ sᴇɴᴅ ᴛʜᴇ **ᴏᴛᴩ** ᴛʜᴀᴛ ʏᴏᴜ'ᴠᴇ ʀᴇᴄᴇɪᴠᴇᴅ ғʀᴏᴍ ᴛᴇʟᴇɢʀᴀᴍ ᴏɴ ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ.\nɪғ ᴏᴛᴩ ɪs `12345`, **ᴩʟᴇᴀsᴇ sᴇɴᴅ ɪᴛ ᴀs** `1 2 3 4 5`."):
        return (str((await client.ask(chat_id=OWNER_ID, text=text, filters=filters.text, timeout=600)).text).replace(' ',''))
    
    async def get_password(text="» ᴩʟᴇᴀsᴇ ᴇɴᴛᴇʀ ʏᴏᴜʀ **ᴛᴡᴏ sᴛᴇᴩ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ** ᴩᴀssᴡᴏʀᴅ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ."):
        status = True
        while status:
            password = (await client.ask(chat_id=OWNER_ID, text=text, filters=filters.text, timeout=300)).text
            try:
                await user_client.check_password(password=password)
                status = False
            except PasswordHashInvalid:
                text = "Wrong password Try Againg !"

    async def signin(phone_number,code_hash,phone_code):
        status = True
        while status:
            try:
                await user_client.sign_in(phone_number, code_hash, phone_code)
                status = False
            except PhoneCodeExpired:
                phone_code = await get_code("Code Expire , Try Againg !")
            except SessionPasswordNeeded:
                await get_password()
            return True
            
    await user_client.connect()
    phone_number = await get_number()
    code = await send_code(phone_number)
    phone_code = await get_code()
    sign = await signin(phone_number, code.phone_code_hash, phone_code)
    if sign:
        session = await user_client.export_session_string()
        await db.add_user_session(session)
        await client.send_message(chat_id=OWNER_ID, text="Login successfully.")
    else:
        await client.send_message(chat_id=OWNER_ID, text="Login failed.")
