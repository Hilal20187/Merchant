import os
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from flask import Flask
import threading

# التوكن يتم جلبه من إعدادات Render
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# القائمة المعتمدة
ALLOWED_USERS = [5040904989, 822007358]
 
ED_USERS = [
    -1004380911690, -1003952714985, -1002470205630, 
    -1004407774851, 1154384855, 822007358, 2065539959
]

sent_messages_map = {}

async def handle_message(update, context):
    try:
        if update.message and update.message.text:
            chat_id_source = update.message.chat_id
            user_id = update.message.from_user.id
            
            # السماح فقط من المجموعة الرئيسية وبواسطة الشخص المعتمد
            if chat_id_source == -1004380911690 and (user_id in ALLOWED_USERS):
                text = update.message.text
                main_msg_id = update.message.message_id
                sent_messages_map[main_msg_id] = {}

                for chat_id in ED_USERS:
                    if chat_id == chat_id_source: continue
                    try:
                        sent_msg = await context.bot.send_message(chat_id=chat_id, text=text)
                        sent_messages_map[main_msg_id][chat_id] = sent_msg.message_id
                    except: pass
    except Exception as e: print(e)

async def delete_msg(update, context):
    try:
        if update.message.reply_to_message:
            target_msg_id = update.message.reply_to_message.message_id
            if target_msg_id in sent_messages_map:
                for chat_id, msg_id in sent_messages_map[target_msg_id].items():
                    try: await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
                    except: pass
                del sent_messages_map[target_msg_id]
            await update.message.reply_to_message.delete()
            await update.message.delete()
    except Exception as e: print(e)

def run_flask():
    Flask(__name__).run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("del", delete_msg))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
