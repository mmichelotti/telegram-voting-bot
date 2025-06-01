
import json
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
TOKEN = "7686518946:AAHNz9AoIHnJHY3BOqHDZgjzMo2k1V5LsqU"
ADMIN_IDS = [365740977]  # Replace with your Telegram user ID

VOTES_FILE = "votes.json"
ITEMS_FILE = "items.json"

def load_data(file_path, default):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return default

def save_data(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f)

votes = load_data(VOTES_FILE, {})
items = load_data(ITEMS_FILE, [
    "Super Robot Ninja Samurai",
    "Teriyaki Western Django",
    "Lino Banfi",
    "Sventura",
    "Super Terremoto Terrore",
    "Uramaki Paranoia"
])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(item, callback_data=f"vote_{item}")] for item in items]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Vote for an item:", reply_markup=reply_markup)

async def vote_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    item = query.data.replace("vote_", "")
    keyboard = [
        [InlineKeyboardButton(str(i), callback_data=f"setvote_{item}_{i}") for i in range(1, 11)]
    ]
    await query.edit_message_text(f"Your vote for: {item}", reply_markup=InlineKeyboardMarkup(keyboard))

async def set_vote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, item, score = query.data.split("_")
    user_id = str(query.from_user.id)
    score = int(score)

    if item not in votes:
        votes[item] = {}
    votes[item][user_id] = score
    save_data(VOTES_FILE, votes)

    avg = sum(votes[item].values()) / len(votes[item])
    await query.edit_message_text(f'Thanks! Current average for "{item}": {avg:.2f}/10')

async def results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "Current Results:\n"
    for item in items:
        item_votes = votes.get(item, {})
        if item_votes:
            avg = sum(item_votes.values()) / len(item_votes)
            text += f"• {item}: {avg:.2f}/10 ({len(item_votes)} votes)\n"
        else:
            text += f"• {item}: No votes yet\n"
    await update.message.reply_text(text)

async def add_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("You are not allowed to add items.")
        return
    item = " ".join(context.args)
    if not item:
        await update.message.reply_text("Usage: /add <item name>")
        return
    if item in items:
        await update.message.reply_text("Item already exists.")
        return
    items.append(item)
    save_data(ITEMS_FILE, items)
    await update.message.reply_text(f"Added item: {item}")

async def remove_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("You are not allowed to remove items.")
        return
    item = " ".join(context.args)
    if not item:
        await update.message.reply_text("Usage: /remove <item name>")
        return
    if item not in items:
        await update.message.reply_text("Item not found.")
        return
    items.remove(item)
    save_data(ITEMS_FILE, items)
    votes.pop(item, None)
    save_data(VOTES_FILE, votes)
    await update.message.reply_text(f"Removed item: {item}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("results", results))
app.add_handler(CommandHandler("add", add_item))
app.add_handler(CommandHandler("remove", remove_item))
app.add_handler(CallbackQueryHandler(vote_menu, pattern="^vote_"))
app.add_handler(CallbackQueryHandler(set_vote, pattern="^setvote_"))

if __name__ == "__main__":
    app.run_polling()
