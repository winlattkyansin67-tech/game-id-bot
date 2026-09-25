import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import telebot
import requests

# Render Port Scan Timeout အတွက် Web Server ဖွင့်ခြင်း
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_http_server, daemon=True).start()

# Telegram Bot Token
TOKEN = '8507984706:AAHI9o5wHyVXfgLaB'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "မင်္ဂလာပါ! MLBB Game ID နဲ့ Server ID ကို ဥပမာ - 123456 (1234) ပုံစံဖြင့် ပို့ပေးပါ။")

@bot.message_handler(func=lambda message: True)
def check_id(message):
    text = message.text.strip()
    if "(" in text and ")" in text:
        try:
            game_id = text.split("(")[0].strip()
            zone_id = text.split("(")[1].replace(")", "").strip()
            
            # API Call
            url = f"https://api.vyturex.com/mlbb?id={game_id}&zone={zone_id}"
            response = requests.get(url).json()
            
            if "name" in response:
                user_name = response["name"]
                bot.reply_to(message, f"✅ Account Found!\n\nName: {user_name}\nID: {game_id} ({zone_id})")
            else:
                bot.reply_to(message, f"❌ Account Not Found!\nID: {game_id} / Server: {zone_id}")
        except Exception as e:
            bot.reply_to(message, "❌ ID စစ်ဆေးရာတွင် အမှားအယွင်း ရှိနေပါသည်။")
    else:
        bot.reply_to(message, "❌ ပုံစံ မမှန်ပါ။ ဥပမာ - 123456 (1234) အတိုင်း ပို့ပေးပါ။")

bot.infinity_polling()
