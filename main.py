import telebot
import random
import json
import os
from telebot import types

BOT_TOKEN = "8255228817:AAGeB7-XMT3MzW3BxnLrK8LzetTCsDD8TJw"
bot = telebot.TeleBot(BOT_TOKEN)

MEMORY_FILE = "bot_brain.json"

def load_brain():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_brain(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

brain = load_brain()
pending_question = {}
user_lang = {}

DICTIONARY = {
    "تحية": ["سلام", "مرحبا", "صباح", "اهلا", "hello", "hi", "bonjour", "salut"],
    "وداع": ["وداعا", "باي", "bye", "au revoir", "goodbye"],
    "شكر": ["شكرا", "thanks", "merci", "مشكور"],
    "منتجات": ["منتج", "عندك", "product", "produit"],
    "سعر": ["سعر", "الثمن", "price", "prix", "how much"],
    "توصيل": ["توصيل", "شحن", "delivery", "livraison"]
}

REPLIES = {
    "تحية": {
        "ar": ["أهلاً! كيف أقدر أساعدك؟"],
        "en": ["Hello! How can I help you?"],
        "fr": ["Bonjour ! Comment puis-je vous aider ?"]
    },
    "وداع": {
        "ar": ["في أمان الله!"],
        "en": ["Goodbye!"],
        "fr": ["Au revoir !"]
    },
    "شكر": {
        "ar": ["العفو!"],
        "en": ["You're welcome!"],
        "fr": ["De rien !"]
    },
    "منتجات": {
        "ar": ["📦 منتجاتنا: قميص 150، جينز 200، حذاء 300 درهم"],
        "en": ["📦 Products: Shirt 150, Jeans 200, Shoes 300 MAD"],
        "fr": ["📦 Produits: Chemise 150, Jean 200, Chaussures 300 MAD"]
    },
    "سعر": {
        "ar": ["💰 القميص 150، الجينز 200، الحذاء 300 درهم."],
        "en": ["💰 Shirt 150, Jeans 200, Shoes 300 MAD."],
        "fr": ["💰 Chemise 150, Jean 200, Chaussures 300 MAD."]
    },
    "توصيل": {
        "ar": ["🚚 توصيل مجاني فوق 300 درهم. 2-3 أيام."],
        "en": ["🚚 Free delivery over 300 MAD. 2-3 days."],
        "fr": ["🚚 Livraison gratuite dès 300 MAD. 2-3 jours."]
    }
}

def get_lang(uid):
    return user_lang.get(uid, None)

def find_intent(text):
    text = text.lower()
    for q in brain:
        if q in text:
            return "brain"
    for intent, words in DICTIONARY.items():
        if any(w in text for w in words):
            return intent
    return None

def generate_reply(uid, text):
    lang = get_lang(uid)
    if not lang:
        return None
    intent = find_intent(text)
    if intent == "brain":
        for q, ans in brain.items():
            if q in text:
                return random.choice(ans.get(lang, list(ans.values())[0]))
    if intent in REPLIES:
        return random.choice(REPLIES[intent].get(lang, REPLIES[intent]["ar"]))
    pending_question[uid] = text
    prompts = {
        "ar": f"❓ لم أفهم: '{text}'. اشرح لي من فضلك.",
        "en": f"❓ I didn't understand: '{text}'. Please explain.",
        "fr": f"❓ Je n'ai pas compris: '{text}'. Expliquez-moi s'il vous plaît."
    }
    return prompts.get(lang, prompts["ar"])

def language_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("🇸🇦 العربية", "🇬🇧 English", "🇫🇷 Français")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if uid in user_lang:
        lang = user_lang[uid]
        welcome_back = {
            "ar": "أهلاً بعودتك! كيف أقدر أساعدك؟",
            "en": "Welcome back! How can I help you?",
            "fr": "Bon retour ! Comment puis-je vous aider ?"
        }
        bot.reply_to(message, welcome_back.get(lang, welcome_back["ar"]))
    else:
        bot.reply_to(message, "👋 مرحباً! Please choose your language / Choisissez votre langue:", reply_markup=language_keyboard())

@bot.message_handler(func=lambda m: True)
def handle(message):
    uid = message.from_user.id
    text = message.text.strip()

    if text == "🇸🇦 العربية":
        user_lang[uid] = "ar"
        bot.reply_to(message, "✅ تم اختيار العربية. تفضل، أنا في خدمتك!")
        return
    elif text == "🇬🇧 English":
        user_lang[uid] = "en"
        bot.reply_to(message, "✅ English selected. How can I help you?")
        return
    elif text == "🇫🇷 Français":
        user_lang[uid] = "fr"
        bot.reply_to(message, "✅ Français choisi. Comment puis-je vous aider ?")
        return

    if uid not in user_lang:
        bot.reply_to(message, "⚠️ الرجاء اختيار لغتك أولاً / Please choose your language first.", reply_markup=language_keyboard())
        return

    lang = user_lang[uid]

    if uid in pending_question:
        question = pending_question.pop(uid)
        if question not in brain:
            brain[question] = {}
        if lang not in brain[question]:
            brain[question][lang] = []
        brain[question][lang].append(text)
        save_brain(brain)
        thanks = {
            "ar": "✅ شكراً! تعلمت شيئاً جديداً.",
            "en": "✅ Thanks! I learned something new.",
            "fr": "✅ Merci ! J'ai appris quelque chose."
        }
        return bot.reply_to(message, thanks.get(lang, thanks["ar"]))

    reply_text = generate_reply(uid, text)
    if reply_text:
        bot.reply_to(message, reply_text)
    else:
        bot.reply_to(message, "⚠️ الرجاء اختيار لغتك أولاً.", reply_markup=language_keyboard())

print("✅ النموذج الأول - النسخة المحسنة يعمل...")
bot.infinity_polling()
