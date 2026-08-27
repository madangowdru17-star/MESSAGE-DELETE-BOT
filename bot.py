import asyncio
import logging
import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot Configuration - Get from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN", "8625791571:AAFi6TCwzK2ug8KE4rdbyuu0NMzG6IqXlWU")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "-1003240507339"))
OWNER_ID = int(os.getenv("OWNER_ID", "7898928200"))

# Data file for persistent storage
DATA_FILE = "bot_data.json"

class AntiAdminBot:
    def __init__(self):
        self.is_active = True
        self.silent_delete = True
        self.deleted_count = 0
        self.banned_admins = []
        self.load_data()
    
    def load_data(self):
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r') as f:
                    data = json.load(f)
                    self.is_active = data.get('is_active', True)
                    self.silent_delete = data.get('silent_delete', True)
                    self.deleted_count = data.get('deleted_count', 0)
                    self.banned_admins = data.get('banned_admins', [])
        except Exception as e:
            logger.error(f"Error loading data: {e}")
    
    def save_data(self):
        try:
            data = {
                'is_active': self.is_active,
                'silent_delete': self.silent_delete,
                'deleted_count': self.deleted_count,
                'banned_admins': self.banned_admins
            }
            with open(DATA_FILE, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.error(f"Error saving data: {e}")

bot_instance = AntiAdminBot()

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    
    if user_id != OWNER_ID:
        await update.message.reply_text("⛔ You are not authorized to use this bot.")
        return
    
    keyboard = [
        [InlineKeyboardButton("🔛 Toggle Bot", callback_data='toggle')],
        [InlineKeyboardButton("🔇 Silent Delete", callback_data='toggle_silent')],
        [InlineKeyboardButton("📊 Status", callback_data='status')],
        [InlineKeyboardButton("📈 Stats", callback_data='stats')],
        [InlineKeyboardButton("➕ Add Admin to Delete", callback_data='add_admin')],
        [InlineKeyboardButton("➖ Remove Admin from Delete", callback_data='remove_admin')],
        [InlineKeyboardButton("📋 Banned Admins List", callback_data='banned_list')],
        [InlineKeyboardButton("🗑️ Clear All Messages", callback_data='clear_all')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    status = "🟢 ACTIVE" if bot_instance.is_active else "🔴 INACTIVE"
    silent = "🔇 ON" if bot_instance.silent_delete else "🔊 OFF"
    
    await update.message.reply_text(
        f"🤖 ANTI-ADMIN BOT\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 Status: {status}\n"
        f"🔇 Silent Delete: {silent}\n"
        f"👥 Banned Admins: {len(bot_instance.banned_admins)}\n"
        f"📢 Channel: {CHANNEL_ID}\n"
        f"👤 Owner: {OWNER_ID}\n"
        f"🗑️ Deleted: {bot_instance.deleted_count} messages\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚠️ Deletes messages from specific admins\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Use buttons below to control:",
        reply_markup=reply_markup
    )

# Button Handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if user_id != OWNER_ID:
        await query.edit_message_text("⛔ You are not authorized.")
        return
    
    if query.data == 'toggle':
        bot_instance.is_active = not bot_instance.is_active
        bot_instance.save_data()
        status = "🟢 ACTIVE" if bot_instance.is_active else "🔴 INACTIVE"
        await query.edit_message_text(f"✅ Bot is now {status}")
    
    elif query.data == 'toggle_silent':
        bot_instance.silent_delete = not bot_instance.silent_delete
        bot_instance.save_data()
        status = "🔇 ON" if bot_instance.silent_delete else "🔊 OFF"
        await query.edit_message_text(f"✅ Silent Delete is now {status}")
    
    elif query.data == 'status':
        status = "🟢 ACTIVE" if bot_instance.is_active else "🔴 INACTIVE"
        silent = "🔇 ON" if bot_instance.silent_delete else "🔊 OFF"
        
        await query.edit_message_text(
            f"📊 BOT STATUS\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📌 Status: {status}\n"
            f"🔇 Silent Delete: {silent}\n"
            f"👥 Banned Admins: {len(bot_instance.banned_admins)}\n"
            f"🗑️ Deleted: {bot_instance.deleted_count}\n"
            f"📢 Channel: {CHANNEL_ID}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💡 Use /addadmin <id> to add admin\n"
            f"💡 Use /removeadmin <id> to remove admin"
        )
    
    elif query.data == 'stats':
        await query.edit_message_text(
            f"📈 STATISTICS\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📌 Status: {'🟢 Active' if bot_instance.is_active else '🔴 Inactive'}\n"
            f"🗑️ Messages Deleted: {bot_instance.deleted_count}\n"
            f"🔇 Silent Mode: {'ON' if bot_instance.silent_delete else 'OFF'}\n"
            f"👥 Banned Admins: {len(bot_instance.banned_admins)}\n"
            f"📢 Monitoring: Channel {CHANNEL_ID}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⏰ Bot is running smoothly!"
        )
    
    elif query.data == 'add_admin':
        await query.edit_message_text(
            "➕ ADD ADMIN TO DELETE LIST\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"To add an admin:\n"
            f"Use: /addadmin <admin_id>\n\n"
            f"Example: /addadmin 123456789\n\n"
            f"⚠️ The admin's messages will be deleted"
        )
    
    elif query.data == 'remove_admin':
        await query.edit_message_text(
            "➖ REMOVE ADMIN FROM DELETE LIST\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"To remove an admin:\n"
            f"Use: /removeadmin <admin_id>\n\n"
            f"Example: /removeadmin 123456789\n\n"
            f"✅ The admin's messages will no longer be deleted"
        )
    
    elif query.data == 'banned_list':
        if bot_instance.banned_admins:
            admin_list = ""
            for admin_id in bot_instance.banned_admins:
                try:
                    admin = await context.bot.get_chat(admin_id)
                    name = admin.full_name or admin.username or str(admin_id)
                    admin_list += f"• {name} (ID: {admin_id})\n"
                except:
                    admin_list += f"• ID: {admin_id}\n"
            
            await query.edit_message_text(
                f"📋 BANNED ADMINS LIST\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"{admin_list}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"Total: {len(bot_instance.banned_admins)} admins"
            )
        else:
            await query.edit_message_text("📋 No admins are currently banned.")
    
    elif query.data == 'clear_all':
        await query.edit_message_text(
            f"⚠️ WARNING!\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"This will delete ALL messages\n"
            f"currently in the channel!\n\n"
            f"Are you sure?\n\n"
            f"⚠️ This action cannot be undone!\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Use: /confirmclear to proceed"
        )

# Add Admin Command
async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("⛔ You are not authorized.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide admin ID\n"
            "Example: /addadmin 123456789"
        )
        return
    
    try:
        admin_id = int(context.args[0])
        if admin_id in bot_instance.banned_admins:
            await update.message.reply_text(f"⚠️ Admin {admin_id} is already in the list.")
            return
        
        bot_instance.banned_admins.append(admin_id)
        bot_instance.save_data()
        await update.message.reply_text(f"✅ Admin {admin_id} added to delete list.")
    except ValueError:
        await update.message.reply_text("❌ Invalid admin ID. Please provide a number.")

# Remove Admin Command
async def remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("⛔ You are not authorized.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide admin ID\n"
            "Example: /removeadmin 123456789"
        )
        return
    
    try:
        admin_id = int(context.args[0])
        if admin_id not in bot_instance.banned_admins:
            await update.message.reply_text(f"⚠️ Admin {admin_id} is not in the list.")
            return
        
        bot_instance.banned_admins.remove(admin_id)
        bot_instance.save_data()
        await update.message.reply_text(f"✅ Admin {admin_id} removed from delete list.")
    except ValueError:
        await update.message.reply_text("❌ Invalid admin ID. Please provide a number.")

# List Banned Admins
async def list_banned(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("⛔ You are not authorized.")
        return
    
    if bot_instance.banned_admins:
        admin_list = "\n".join([f"• {admin_id}" for admin_id in bot_instance.banned_admins])
        await update.message.reply_text(
            f"📋 BANNED ADMINS LIST\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{admin_list}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Total: {len(bot_instance.banned_admins)} admins"
        )
    else:
        await update.message.reply_text("📋 No admins are currently banned.")

# Confirm Clear
async def confirm_clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("⛔ You are not authorized.")
        return
    
    try:
        await update.message.reply_text(
            "🗑️ Deleting all messages...\n"
            "⚠️ Note: Only future messages can be auto-deleted.\n"
            "Past messages must be deleted manually."
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# Status Command
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("⛔ You are not authorized.")
        return
    
    status = "🟢 ACTIVE" if bot_instance.is_active else "🔴 INACTIVE"
    silent = "🔇 ON" if bot_instance.silent_delete else "🔊 OFF"
    
    await update.message.reply_text(
        f"📊 BOT STATUS\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 Status: {status}\n"
        f"🔇 Silent Delete: {silent}\n"
        f"👥 Banned Admins: {len(bot_instance.banned_admins)}\n"
        f"🗑️ Deleted: {bot_instance.deleted_count}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Use /start for control panel."
    )

# Toggle Command
async def toggle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("⛔ You are not authorized.")
        return
    
    bot_instance.is_active = not bot_instance.is_active
    bot_instance.save_data()
    status = "🟢 ACTIVE" if bot_instance.is_active else "🔴 INACTIVE"
    await update.message.reply_text(f"✅ Bot is now {status}")

# Handle Channel Messages
async def handle_channel_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.channel_post and update.channel_post.chat_id == CHANNEL_ID:
        message = update.channel_post
        user_id = message.from_user.id if message.from_user else None
        
        if not bot_instance.is_active:
            return
        
        if user_id == OWNER_ID:
            return
        
        if user_id in bot_instance.banned_admins:
            try:
                await message.delete()
                bot_instance.deleted_count += 1
                bot_instance.save_data()
                
                logger.info(f"🗑️ Deleted message from banned admin {user_id}")
                
                if not bot_instance.silent_delete:
                    try:
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=f"⚠️ Your message was deleted because you're banned."
                        )
                    except:
                        pass
                
            except Exception as e:
                logger.error(f"Failed to delete message: {e}")

# Handle All Messages
async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.channel_post and update.channel_post.chat_id == CHANNEL_ID:
        await handle_channel_message(update, context)

# Error Handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Update {update} caused error {context.error}")

# Main Async Function
async def main_async():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("toggle", toggle))
    application.add_handler(CommandHandler("addadmin", add_admin))
    application.add_handler(CommandHandler("removeadmin", remove_admin))
    application.add_handler(CommandHandler("listbanned", list_banned))
    application.add_handler(CommandHandler("confirmclear", confirm_clear))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(
        filters.ALL & ~filters.COMMAND,
        handle_all_messages
    ))
    application.add_error_handler(error_handler)
    
    print("🚀 ANTI-ADMIN BOT STARTING...")
    print("━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"📱 Bot Token: {BOT_TOKEN[:10]}...")
    print(f"📱 Monitoring channel: {CHANNEL_ID}")
    print(f"👤 Owner ID: {OWNER_ID}")
    print(f"✅ Bot is {'ACTIVE' if bot_instance.is_active else 'INACTIVE'}")
    print(f"🔇 Silent delete: {'ON' if bot_instance.silent_delete else 'OFF'}")
    print(f"👥 Banned Admins: {len(bot_instance.banned_admins)}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━")
    print("💡 Bot is now running...")
    print("💡 Press Ctrl+C to stop")
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped")
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()

def main():
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped")

if __name__ == '__main__':
    main()
