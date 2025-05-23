import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup # type: ignore
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes # type: ignore
from zLocket_Tool import zLocket

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token - Thay YOUR_BOT_TOKEN bằng token bot của bạn
TOKEN = "7986646989:AAHaqGYifjZE73TQbukVA_DUk69UIQ9PBOk"

# Store active attacks
active_attacks = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    keyboard = [
        [InlineKeyboardButton("🎯 Tấn công Locket", callback_data='attack')],
        [InlineKeyboardButton("ℹ️ Thông tin Tool", callback_data='info')],
        [InlineKeyboardButton("❌ Dừng tấn công", callback_data='stop')],
        [InlineKeyboardButton("/banggia", callback_data='banggia')],
        [InlineKeyboardButton("/key", callback_data='key')],
        [InlineKeyboardButton("/removekey", callback_data='removekey')],
        [InlineKeyboardButton("/info", callback_data='info')],
        [InlineKeyboardButton("/ngl", callback_data='ngl')],
        [InlineKeyboardButton("/locket", callback_data='locket')],
        [InlineKeyboardButton("/sms", callback_data='sms')],
        [InlineKeyboardButton("/changename", callback_data='changename')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        '👋 Chào mừng đến với zLocket Tool Pro!\n'
        'Sử dụng các nút bên dưới để điều khiển tool:',
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses."""
    query = update.callback_query
    await query.answer()

    if query.data == 'attack':
        await query.message.reply_text(
            '🎯 Vui lòng nhập username hoặc link Locket target:'
        )
        context.user_data['waiting_for_target'] = True
    
    elif query.data == 'info':
        await query.message.reply_text(
            'ℹ️ zLocket Tool Pro\n'
            'Version: 1.0.6\n'
            'Author: @wus_team\n'
            'Github: https://github.com/wusthanhdieu\n\n'
            '📝 Hướng dẫn sử dụng:\n'
            '1. Nhấn "Tấn công Locket"\n'
            '2. Nhập username hoặc link Locket target\n'
            '3. Đợi kết quả tấn công\n'
            '4. Có thể dừng tấn công bất cứ lúc nào'
        )
    
    elif query.data == 'stop':
        user_id = update.effective_user.id
        if user_id in active_attacks:
            active_attacks[user_id] = False
            await query.message.reply_text('🛑 Đã dừng tấn công!')
        else:
            await query.message.reply_text('❌ Không có tấn công nào đang chạy!')
    
    elif query.data == 'banggia':
        await banggia(update, context)
    elif query.data == 'key':
        await query.message.reply_text('/key')
        await query.message.reply_text('🔑 Vui lòng nhập key để kích hoạt:')
        context.user_data['waiting_for_key'] = True
    elif query.data == 'removekey':
        await query.message.reply_text('/removekey')
        await removekey(update, context)
    elif query.data == 'ngl':
        await query.message.reply_text('/ngl')
        await query.message.reply_text('🚀 Vui lòng nhập username và message (cách nhau bởi dấu |):')
        context.user_data['waiting_for_ngl'] = True
    elif query.data == 'locket':
        await query.message.reply_text('/locket')
        await query.message.reply_text('🎯 Vui lòng nhập link và thời gian (cách nhau bởi dấu |):')
        context.user_data['waiting_for_locket'] = True
    elif query.data == 'sms':
        await query.message.reply_text('/sms')
        await query.message.reply_text('📱 Vui lòng nhập số điện thoại và số lượng (cách nhau bởi dấu |):')
        context.user_data['waiting_for_sms'] = True
    elif query.data == 'changename':
        await query.message.reply_text('/changename')
        await query.message.reply_text('✏️ Vui lòng nhập link, tên mới và thời gian (cách nhau bởi dấu |):')
        context.user_data['waiting_for_changename'] = True

def extract_locket_uid(text: str) -> str:
    """Extract Locket UID from text or link."""
    # If it's a direct UID
    if text.isalnum():
        return text
    
    # If it's a Locket link
    if 'locket' in text.lower():
        # Try to extract UID from various Locket link formats
        parts = text.split('/')
        for part in parts:
            if part.isalnum() and len(part) > 5:
                return part
    
    return text

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages."""
    user_id = update.effective_user.id
    text = update.message.text
    # Xử lý nhập key
    if context.user_data.get('waiting_for_key'):
        key = text.strip()
        # TODO: Thay bằng logic kiểm tra key thực tế
        if key == '123456':
            context.user_data['key_activated'] = True
            await update.message.reply_text('✅ Key hợp lệ! Bạn đã được kích hoạt.')
        else:
            await update.message.reply_text('❌ Key không hợp lệ!')
        context.user_data['waiting_for_key'] = False
        return
    # Xử lý nhập NGL
    if context.user_data.get('waiting_for_ngl'):
        try:
            username, message = [x.strip() for x in text.split('|', 1)]
            # TODO: Thực hiện spam NGL thật sự
            await update.message.reply_text(f'🚀 Đã spam NGL cho {username} với nội dung: {message}')
        except Exception:
            await update.message.reply_text('❌ Sai định dạng! Vui lòng nhập: username|message')
        context.user_data['waiting_for_ngl'] = False
        return
    # Xử lý nhập locket
    if context.user_data.get('waiting_for_locket'):
        try:
            link, time = [x.strip() for x in text.split('|', 1)]
            # TODO: Thực hiện spam Locket thật sự
            await update.message.reply_text(f'🎯 Đã spam Locket: {link} trong {time}s')
        except Exception:
            await update.message.reply_text('❌ Sai định dạng! Vui lòng nhập: link|thời gian')
        context.user_data['waiting_for_locket'] = False
        return
    # Xử lý nhập sms
    if context.user_data.get('waiting_for_sms'):
        try:
            phone, amount = [x.strip() for x in text.split('|', 1)]
            # TODO: Thực hiện spam SMS thật sự
            await update.message.reply_text(f'📱 Đã spam SMS tới {phone} số lượng {amount}')
        except Exception:
            await update.message.reply_text('❌ Sai định dạng! Vui lòng nhập: số điện thoại|số lượng')
        context.user_data['waiting_for_sms'] = False
        return
    # Xử lý nhập changename
    if context.user_data.get('waiting_for_changename'):
        try:
            link, newname, time = [x.strip() for x in text.split('|', 2)]
            # TODO: Thực hiện đổi tên Locket thật sự
            await update.message.reply_text(f'✏️ Đã đổi tên Locket {link} thành {newname} trong {time}s')
        except Exception:
            await update.message.reply_text('❌ Sai định dạng! Vui lòng nhập: link|tên mới|thời gian')
        context.user_data['waiting_for_changename'] = False
        return
    # Xử lý tấn công Locket như cũ
    if context.user_data.get('waiting_for_target'):
        target = text
        target_uid = extract_locket_uid(target)
        
        status_message = await update.message.reply_text(
            f'🎯 Đang tấn công target: {target}\n'
            f'UID: {target_uid}\n'
            '⏳ Vui lòng đợi...'
        )
        
        # Initialize zLocket tool
        try:
            locket = zLocket(target_friend_uid=target_uid)
            active_attacks[user_id] = True
            
            # Start the attack
            await status_message.edit_text(
                f'🎯 Đang tấn công target: {target}\n'
                f'UID: {target_uid}\n'
                '⚡️ Đang khởi tạo...'
            )
            
            # Run setup in a separate thread to avoid blocking
            def run_attack():
                try:
                    locket.setup()
                    return True
                except Exception as e:
                    logger.error(f"Attack error: {str(e)}")
                    return False
            
            # Run the attack
            success = await asyncio.get_event_loop().run_in_executor(None, run_attack)
            
            if success and active_attacks.get(user_id, False):
                await status_message.edit_text(
                    f'✅ Tấn công thành công!\n'
                    f'Target: {target}\n'
                    f'UID: {target_uid}'
                )
            else:
                if not active_attacks.get(user_id, False):
                    await status_message.edit_text('🛑 Tấn công đã bị dừng!')
                else:
                    await status_message.edit_text('❌ Tấn công thất bại!')
            
        except Exception as e:
            await status_message.edit_text(f'❌ Lỗi: {str(e)}')
        
        finally:
            context.user_data['waiting_for_target'] = False
            if user_id in active_attacks:
                del active_attacks[user_id]
    else:
        await update.message.reply_text(
            'Vui lòng sử dụng các lệnh có sẵn hoặc nhấn /start để xem menu.'
        )

async def banggia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "💰 <b>Bảng giá Key</b> 💰\n\n"
        "<b>Các gói chính:</b>\n"
        "<pre>"
        "| Key gói        | Giá      | Số lượt dùng | Giá mỗi lượt |\n"
        "|----------------|----------|--------------|--------------|\n"
        "| Gói cơ bản     | 20.000đ  | 100 lượt     | 200đ/lượt    |\n"
        "| Gói phổ thông  | 50.000đ  | 300 lượt     | 167đ/lượt    |\n"
        "| Gói nâng cao   | 100.000đ | 800 lượt     | 125đ/lượt    |\n"
        "</pre>\n"
        "<b>Gói bổ sung lượt dùng:</b>\n"
        "<pre>"
        "| Gói bổ sung | Giá     | Lượt thêm | Ghi chú      |\n"
        "|-------------|---------|-----------|--------------|\n"
        "| 10 lượt     | 5.000đ  | 10        | 500đ/lượt    |\n"
        "| 50 lượt     | 20.000đ | 50        | 400đ/lượt    |\n"
        "| 100 lượt    | 35.000đ | 100       | 350đ/lượt    |\n"
        "</pre>\n"
        "🎁 <b>Lượt dùng miễn phí:</b>\n"
        "- Bot tự động phát key miễn phí mỗi 12h (12h trưa và 12h đêm)\n"
        "- Số lượt dùng ngẫu nhiên từ 2-3 lượt\n"
        "- Đối với những người đã có key chính, key tự động sẽ cộng thêm số lượt dùng vào key chính\n"
        "- Key tự động bị xóa sau khi hết lượt dùng\n\n"
        "⚠️ <b>Lưu ý:</b>\n"
        "- Giá đã bao gồm phí duy trì API\n"
        "- Key không giới hạn thời gian sử dụng\n"
        "- Có thể mua thêm lượt cho key đang dùng\n"
        "- Key miễn phí có thể cộng lượt vào key chính\n"
    )
    await update.message.reply_text(text, parse_mode='HTML')

async def key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔑 Vui lòng nhập key để kích hoạt.")

async def removekey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🗑️ Key của bạn đã được xóa.")

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ℹ️ Thông tin key và lượt dùng của bạn.")

async def ngl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Spam NGL thành công!")

async def locket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎯 Đã gửi spam Locket!")

async def sms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📱 Đã gửi spam SMS!")

async def changename(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✏️ Đã đổi tên Locket!")

def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main() 