import os
import json
import random
from telegram import Update, ChatPermissions
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = "8254178367:AAFrmjTudwyMxvo82DwD7gGvD6QAdOfOnOU"

WELCOME_FOLDER = "welcome"
COMMAND_FILE = "commands.json"

DEFAULT_COMMANDS = {
    "كشف": "info",
    "كتم": "mute",
    "فك": "unmute",
    "طرد": "ban",
    "مسح المكتومين": "clear_mute"
}


# ======================
# تحميل الأوامر
# ======================
def load_commands():
    if not os.path.exists(COMMAND_FILE):
        with open(COMMAND_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_COMMANDS, f, ensure_ascii=False, indent=2)
    with open(COMMAND_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_commands(data):
    with open(COMMAND_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


commands = load_commands()


# ======================
# الترحيب
# ======================
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for user in update.message.new_chat_members:
        photos = os.listdir(WELCOME_FOLDER)
        photo = random.choice(photos)

        text = f"""
👋 مرحباً {user.full_name}

🆔 `{user.id}`
🔗 @{user.username if user.username else "لا يوجد"}

🤍 نورت المجموعة
"""

        await context.bot.send_photo(
            update.effective_chat.id,
            open(f"{WELCOME_FOLDER}/{photo}", "rb"),
            caption=text,
            parse_mode="Markdown"
        )


# ======================
# كشف
# ======================
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.reply_to_message.from_user if update.message.reply_to_message else update.effective_user
    await update.message.reply_text(
        f"👤 {user.full_name}\n🆔 `{user.id}`",
        parse_mode="Markdown"
    )


# ======================
# كتم
# ======================
async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return
    user = update.message.reply_to_message.from_user

    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        user.id,
        ChatPermissions(can_send_messages=False)
    )
    await update.message.reply_text("🔇 تم كتم العضو")


# ======================
# فك كتم
# ======================
async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return
    user = update.message.reply_to_message.from_user

    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        user.id,
        ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True
        )
    )
    await update.message.reply_text("🔊 تم فك الكتم")


# ======================
# مسح المكتومين
# ======================
async def clear_mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    count = 0

    admins = await context.bot.get_chat_administrators(chat_id)

    for admin in admins:
        try:
            await context.bot.restrict_chat_member(
                chat_id,
                admin.user.id,
                ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True
                )
            )
            count += 1
        except:
            pass

    await update.message.reply_text(f"✅ تم مسح الكتم عن {count} عضو")


# ======================
# طرد
# ======================
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return
    user = update.message.reply_to_message.from_user

    await context.bot.ban_chat_member(
        update.effective_chat.id,
        user.id
    )
    await update.message.reply_text("🚫 تم طرد العضو")


# ======================
# تغيير الأوامر
# ======================
async def change_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.replace("تغيير", "").strip().split()

    if len(text) != 2:
        return await update.message.reply_text("استخدم:\nتغيير كتم اسكات")

    old, new = text
    if old not in commands:
        return await update.message.reply_text("❌ الأمر غير موجود")

    commands[new] = commands.pop(old)
    save_commands(commands)

    await update.message.reply_text(f"✅ تم تغيير الأمر:\n{old} ⟶ {new}")


# ======================
# استقبال الأوامر
# ======================
async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text.startswith("تغيير"):
        return await change_command(update, context)

    if text in commands:
        func = commands[text]

        if func == "info":
            await info(update, context)
        elif func == "mute":
            await mute(update, context)
        elif func == "unmute":
            await unmute(update, context)
        elif func == "ban":
            await ban(update, context)
        elif func == "clear_mute":
            await clear_mute(update, context)


# ======================
# تشغيل
# ======================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))

    print("✅ البوت يعمل بنجاح")
    app.run_polling()


if __name__ == "__main__":
    main()