from pyrogram import Client, filters, enums
from pyrogram.types import Message

@Client.on_message(filters.outgoing & filters.command('alive'))
async def alive(client: Client, message: Message):
    await message.reply_text("I'm Alive")
