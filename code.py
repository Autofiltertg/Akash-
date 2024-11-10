import asyncio
import emoji
import mimetypes
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaWebPage

api_id = '11756133'
api_hash = '6d2d5c9ca4fa62699f50feec4edd7b39'
bot_token = '7268133849:AAGgIPmfOG_MYJf_aQs3siKKhB94DEm8gDs'

source_channel_id = -1002489619196
destination_channel_id = -1002307986808
forwarding_channel_id = -1002336664104

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)
message_queue = asyncio.Queue()

def is_emoji_only(text):
    return all(emoji.is_emoji(char) for char in text)

@bot.on(events.NewMessage(chats=source_channel_id))
async def handler(event):
    await message_queue.put(event)

async def process_queue():
    while True:
        await asyncio.sleep(0.1)
        event = await message_queue.get()
        print(f"Processing message from {source_channel_id}: {event.message.text}")
        
        delete_message = False
        
        if event.message.sticker:
            print("Sticker detected, forwarding and deleting...")
            await bot.send_message(forwarding_channel_id, event.message)
            delete_message = True
        elif event.message.gif:
            print("GIF detected, forwarding and deleting...")
            await bot.send_message(forwarding_channel_id, event.message)
            delete_message = True
        elif event.message.text and is_emoji_only(event.message.text):
            print("Emoji-only message detected, forwarding and deleting...")
            await bot.send_message(forwarding_channel_id, event.message.text)
            delete_message = True
        elif event.message.media:
            file_name = "File"
            
            if event.message.photo:
                print("Photo detected, forwarding and deleting...")
                await bot.send_file(forwarding_channel_id, event.message.media, caption="⚠️ Forbidden photo detected")
                delete_message = True
            elif hasattr(event.message.media, 'document'):
                mime_type = event.message.media.document.mime_type
                for attribute in event.message.media.document.attributes:
                    if hasattr(attribute, 'file_name'):
                        file_name = attribute.file_name
                        break

                if mime_type and mime_type.startswith("image/"):
                    print("Image file detected, forwarding and deleting...")
                    await bot.send_file(forwarding_channel_id, event.message.media, caption="⚠️ Forbidden image file detected")
                    delete_message = True
                elif any(keyword in file_name for keyword in ['https', 't.me', '@']):
                    print(f"File contains forbidden keywords: {file_name}. Forwarding and deleting...")
                    await bot.send_file(forwarding_channel_id, event.message.media, caption=f"⚠️ Forbidden content detected: {file_name}")
                    delete_message = True
                else:
                    new_caption = f"📁 Filename: {file_name}"
                    await bot.send_file(destination_channel_id, event.message.media, caption=new_caption)
                    try:
                        await event.edit(new_caption)
                    except Exception as e:
                        print(f"Failed to edit message caption: {e}")
            elif isinstance(event.message.media, MessageMediaWebPage):
                print("Link preview detected, forwarding with preview and deleting...")
                await bot.send_message(forwarding_channel_id, event.message.text, link_preview=True)
                delete_message = True
        elif event.message.text:
            forbidden_keywords = ['https', 'http', 't.me', '@']
            if any(keyword in event.message.text for keyword in forbidden_keywords):
                print(f"Text contains forbidden keywords or links: {event.message.text}. Forwarding and deleting with preview...")
                await bot.send_message(forwarding_channel_id, event.message.text, link_preview=True)
                delete_message = True
            elif not event.message.media:
                print(f"Message without media detected: {event.message.text}. Marking as forbidden and deleting...")
                await bot.send_message(forwarding_channel_id, f"⚠️ Forbidden message: {event.message.text}")
                delete_message = True
            else:
                await bot.send_message(destination_channel_id, event.message.text)

        if delete_message:
            await event.delete()

        message_queue.task_done()

async def main():
    print("Bot Started ✅ ~Coded By 𝐎𝐛𝐢𝐭𝐨")
    bot.loop.create_task(process_queue())
    await bot.run_until_disconnected()

with bot:
    bot.loop.run_until_complete(main())
    
