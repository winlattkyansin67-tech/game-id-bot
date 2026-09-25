import os
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
import requests

# 1. Render Port Timeout မဖြစ်စေရန် HTTP Server
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is live!")

def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_http_server, daemon=True).start()

# 2. Telegram Bot Configuration
TOKEN = '8507984706:AAHI9o5wHyVXfgLaBqf9CFeH1zgcTvfsmuo'
bot = telebot.TeleBot(TOKEN)

# 3. Webhook အဟောင်း ငြိနေသည်များကို ရှင်းထုတ်ခြင်း
try:
    bot.remove_webhook()
    time.sleep(1)
except Exception:
    pass

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "မင်္ဂလာပါ! MLBB Game ID နဲ့ Server ID ကို ဥပမာ - 123456 (1234) ပုံစံဖြင့် ပို့ပေးပါ။")

@bot.message_handler(func=lambda message: True)
def check_id(message):
    text = message.text.strip()
    if "(" in text and ")" in text:
        try:
            game_id = text.split("(")[0].strip()
            zone_id = text.split("(")[1].replace(")", "").strip()
            
            url = f"https://api.vyturex.com/mlbb?id={game_id}&zone={zone_id}"
            response = requests.get(url, timeout=10).json()
            
            if "name" in response:
                user_name = response["name"]
                bot.reply_to(message, f"✅ Account Found!\n\nName: {user_name}\nID: {game_id} ({zone_id})")
            else:
                bot.reply_to(message, f"❌ Account Not Found!\nID: {game_id} / Server: {zone_id}")
        except Exception:
            bot.reply_to(message, "❌ ID စစ်ဆေးရာတွင် အမှားအယွင်း ရှိနေပါသည်။")
    else:
        bot.reply_to(message, "❌ ပုံစံ မမှန်ပါ။ ဥပမာ - 123456 (1234) အတိုင်း ပို့ပေးပါ။")

# 4. Connection မပြတ်သွားစေရန် Loop ဖြင့် စောင့်ကြည့်ခြင်း
while True:
    try:
        bot.polling(none_stop=True, interval=1, timeout=60)
    except Exception as e:
        time.sleep(5)
