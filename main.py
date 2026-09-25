import telebot
import requests

TOKEN = '8507984706:AAHI9o5wHyVXfgLaBqf9CFeH1zgcTvfsmuo'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "မင်္ဂလာပါ! Mobile Legends ID စစ်ရန် ID နှင့် Server ID ကို ပို့ပေးပါ။\n\nဥပမာ - 1549229928 (16507)")

@bot.message_handler(func=lambda message: True)
def check_id(message):
    text = message.text.strip()
    
    # ID နှင့် Server ID ကို ခွဲထုတ်ခြင်း
    if "(" in text and ")" in text:
        try:
            game_id = text.split("(")[0].strip()
            zone_id = text.split("(")[1].replace(")", "").strip()
            
            # MLBB Checker API သို့ လှမ်းတောင်းခြင်း
            url = f"https://api.vytx.org/mlbb?id={game_id}&zone={zone_id}"
            res = requests.get(url).json()
            
            if res.get("status") == True or "username" in res:
                name = res.get("username", "N/A")
                
                # ပုံထဲကအတိုင်း ပြန်လည် ထုတ်ပေးမည့် Message ပုံစံ
                reply_msg = (
                    f"🎮 **Mobile Legends Bang Bang**\n"
                    f"━━━━━━━━━━━━━━━━━━━\n"
                    f"👤 **Name:** {name}\n"
                    f"🆔 **ID:** {game_id}\n"
                    f"🌐 **Server:** {zone_id}\n"
                    f"🇲🇲 **Region:** Myanmar\n"
                    f"━━━━━━━━━━━━━━━━━━━"
                )
                bot.reply_to(message, reply_msg, parse_mode="Markdown")
            else:
                bot.reply_to(message, "❌ ဂိမ်း ID သို့မဟုတ် Server ID မှားယွင်းနေပါသည်။ ပြန်စစ်ပေးပါ။")
                
        except Exception as e:
            bot.reply_to(message, "❌ ID စစ်ဆေးရာတွင် အမှားအယွင်း ရှိနေပါသည်။ ပုံစံအတိုင်း ပြန်ပို့ပေးပါ (ဥပမာ - 123456 (1234))")
    else:
        bot.reply_to(message, "💡 ကျေးဇူးပြု၍ `ID (ServerID)` ပုံစံဖြင့် ပို့ပေးပါ။\nဥပမာ - `1549229928 (16507)`")

print("Bot is running...")
bot.polling(none_stop=True)
