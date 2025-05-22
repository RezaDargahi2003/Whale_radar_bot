# whale_bot_ai.py

import telebot
from telebot import types
from config import TELEGRAM_TOKEN, PRICING, WELCOME_MESSAGE, ADMIN_ID
from datetime import datetime, timedelta

bot = telebot.TeleBot(TELEGRAM_TOKEN)

user_subscriptions = {}  # برای ذخیره‌سازی وضعیت اشتراک کاربران

def is_subscribed(user_id):
    if user_id in user_subscriptions:
        return datetime.now() < user_subscriptions[user_id]
    return False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    bot.send_message(user_id, WELCOME_MESSAGE, parse_mode='Markdown')

@bot.message_handler(commands=['subscribe'])
def show_subscription_options(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('ماهانه', 'شش ماهه', 'سالانه')
    bot.send_message(message.chat.id, "لطفا نوع اشتراک را انتخاب کنید:", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text in ['ماهانه', 'شش ماهه', 'سالانه'])
def handle_subscription_selection(message):
    duration_map = {
        'ماهانه': ('monthly', 30),
        'شش ماهه': ('6months', 180),
        'سالانه': ('yearly', 365)
    }
    key, days = duration_map[message.text]
    amount = PRICING[key]
    user_subscriptions[message.from_user.id] = datetime.now() + timedelta(days=days)
    bot.send_message(message.chat.id, f'✅ اشتراک شما برای {days} روز فعال شد.')

@bot.message_handler(commands=['signal'])
def get_signal_request(message):
    if not is_subscribed(message.from_user.id):
        bot.send_message(message.chat.id, "اشتراک شما فعال نیست. لطفاً با /subscribe اشتراک تهیه کنید.")
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('هوشمند', 'دستی')
    bot.send_message(message.chat.id, "نوع دریافت سیگنال را انتخاب کنید:", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == 'هوشمند')
def smart_signal(message):
    # نمونه ساده سیگنال هوشمند
    bot.send_message(message.chat.id, "📈 سیگنال هوشمند: BTC در محدوده حمایتی قرار دارد. احتمال رشد.")

@bot.message_handler(func=lambda msg: msg.text == 'دستی')
def ask_symbol(message):
    msg = bot.send_message(message.chat.id, "نام ارز موردنظر را وارد کنید (مثلاً BTC):")
    bot.register_next_step_handler(msg, send_manual_signal)

def send_manual_signal(message):
    symbol = message.text.upper()
    bot.send_message(message.chat.id, f"📊 سیگنال برای {symbol}:\n- وضعیت: خرید در حمایت\n- تایم‌فریم: 1 ساعته")

@bot.message_handler(commands=['status'])
def check_status(message):
    if is_subscribed(message.from_user.id):
        expiry = user_subscriptions[message.from_user.id]
        bot.send_message(message.chat.id, f"✅ اشتراک شما تا {expiry.strftime('%Y-%m-%d %H:%M')} معتبر است.")
    else:
        bot.send_message(message.chat.id, "❌ شما اشتراک فعالی ندارید.")

print("ربات در حال اجراست...")
bot.infinity_polling()
