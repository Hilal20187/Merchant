import os
import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from flask import Flask, request
from telegram import Update
import threading

BOT_TOKEN = os.environ.get("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 10000))

ALLOWED_USERS = [5040904989, 822007358]
ED_USERS = [-1004380911690, -1003952714985, -1002470205630, -1004407774851, 1154384855, 822007358, 2065539959]

sent_messages_map = {}
app_flask = Flask(__name__)
bot_app = Application.builder().token(BOT_TOKEN).build()

async def handle_message(update, context):
    if update.message and update.message.text:
        chat_id_source = update.message.chat_id
        user_id = update.message.from_user.id
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

async def delete_msg(update, context):
    if update.message.reply_to_message:
        target_msg_id = update.message.reply_to_message.message_id
        if target_msg_id in sent_messages_map:
            for chat_id, msg_id in sent_messages_map[target_msg_id].items():
                try: await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
                except: pass
            del sent_messages_map[target_msg_id]
        await update.message.reply_to_message.delete()
        await update.message.delete()

bot_app.add_handler(CommandHandler("del", delete_msg))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@app_flask.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    threading.Thread(target=bot_app.process_update, args=(update,)).start()
    return "OK"

if __name__ == "__main__":
    bot_app.bot.set_webhook(f"https://merchant-osew.onrender.com/{BOT_TOKEN}")
    app_flask.run(host='0.0.0.0', port=PORT)
 
