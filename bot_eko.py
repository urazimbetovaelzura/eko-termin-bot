import os
import json
import asyncio
from collections import defaultdict, deque
from pathlib import Path
from aiohttp import web

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode


# ================== НАСТРОЙКИ ==================
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError(
        "BOT_TOKEN не найден. Добавьте переменную BOT_TOKEN в Render "
        "или укажите токен в переменных окружения."
    )

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

BASE_DIR = Path(__file__).resolve().parent
TERMS_FILE = BASE_DIR / "terms.json"

# Хранение выбранного языка пользователя
user_lang = {}

# История поиска пользователя
history = defaultdict(lambda: deque(maxlen=5))


# ================== ЗАГРУЗКА ТЕРМИНОВ ==================
def load_terms():
    with open(TERMS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


terms = load_terms()


# ================== ТЕКСТЫ И КНОПКИ ==================
LANG_TEXTS = {
    "qq": {
        "welcome": "🌿 <b>Ekologiyalıq atamalar maǵlıwmatnamasına xosh kelipsiz!</b>\n\nInterfeys tilin saylań:",
        "selected": "✅ Til saylandı: <b>Qaraqalpaq</b>\n\nEndi ekologiyalıq atamanı kirgiziń.",
        "search": "🔎 Ekologiyalıq atamanı kirgiziń.",
        "list": "📚 Atamalar dizimi",
        "history": "🕘 Izlew tariyxı",
        "help": (
            "ℹ️ <b>Botтан paydalanıw tártibi:</b>\n\n"
            "Atamanı rus, ingliz, ózbek yamasa qaraqalpaq tilinde kirgiziń. "
            "Bot atamanı tawıp, saylanǵan tilde anıqlamasın kórsetedi.\n\n"
            "Túymeler: izlew, atamalar dizimi, tariyx, járdem, tildi ózgertiw."
        ),
        "not_found": "❌ <b>Atama tabılmadı.</b>\n\nJazılıwın tekseriń yamasa atamalar dizimin ashıń.",
        "choose": "🌐 Aldın tildi saylań.",
        "term_label": "🌿 <b>Atama:</b>",
        "def_label": "📘 <b>Anıqlama:</b>",
        "empty_history": "🕘 Izlew tariyxı bos.",
        "restart": "🔄 Bot qaytadan baslandı. Tildi saylań:",
    },
    "ru": {
        "welcome": "🌿 <b>Добро пожаловать в справочник экологических терминов!</b>\n\nВыберите язык интерфейса:",
        "selected": "✅ Язык выбран: <b>Русский</b>\n\nТеперь введите экологический термин.",
        "search": "🔎 Введите экологический термин.",
        "list": "📚 Список терминов",
        "history": "🕘 История поиска",
        "help": (
            "ℹ️ <b>Как пользоваться ботом:</b>\n\n"
            "Введите термин на русском, английском, узбекском или каракалпакском языке. "
            "Бот найдёт термин и покажет определение на выбранном языке.\n\n"
            "Кнопки меню: поиск, список терминов, история, помощь, смена языка."
        ),
        "not_found": "❌ <b>Термин не найден.</b>\n\nПроверьте написание или откройте список терминов.",
        "choose": "🌐 Пожалуйста, сначала выберите язык.",
        "term_label": "🌿 <b>Термин:</b>",
        "def_label": "📘 <b>Определение:</b>",
        "empty_history": "🕘 История поиска пуста.",
        "restart": "🔄 Бот перезапущен. Выберите язык:",
    },
    "en": {
        "welcome": "🌿 <b>Welcome to the ecological terms directory!</b>\n\nChoose the interface language:",
        "selected": "✅ Language selected: <b>English</b>\n\nNow enter an ecological term.",
        "search": "🔎 Enter an ecological term.",
        "list": "📚 Term list",
        "history": "🕘 Search history",
        "help": (
            "ℹ️ <b>How to use the bot:</b>\n\n"
            "Enter a term in Russian, English, Uzbek or Karakalpak. "
            "The bot will find the term and show the definition in the selected language."
        ),
        "not_found": "❌ <b>Term not found.</b>\n\nCheck the spelling or open the term list.",
        "choose": "🌐 Please choose a language first.",
        "term_label": "🌿 <b>Term:</b>",
        "def_label": "📘 <b>Definition:</b>",
        "empty_history": "🕘 Search history is empty.",
        "restart": "🔄 Bot restarted. Choose language:",
    },
    "uz": {
        "welcome": "🌿 <b>Ekologik atamalar ma'lumotnomasiga xush kelibsiz!</b>\n\nInterfeys tilini tanlang:",
        "selected": "✅ Til tanlandi: <b>O‘zbek</b>\n\nEndi ekologik atamani kiriting.",
        "search": "🔎 Ekologik atamani kiriting.",
        "list": "📚 Atamalar ro‘yxati",
        "history": "🕘 Qidiruv tarixi",
        "help": (
            "ℹ️ <b>Botdan foydalanish tartibi:</b>\n\n"
            "Atamani rus, ingliz, o‘zbek yoki qoraqalpoq tilida kiriting. "
            "Bot atamani topib, tanlangan tilda ta’rifini ko‘rsatadi."
        ),
        "not_found": "❌ <b>Atama topilmadi.</b>\n\nImlo tekshiring yoki atamalar ro‘yxatini oching.",
        "choose": "🌐 Avval tilni tanlang.",
        "term_label": "🌿 <b>Atama:</b>",
        "def_label": "📘 <b>Ta’rif:</b>",
        "empty_history": "🕘 Qidiruv tarixi bo‘sh.",
        "restart": "🔄 Bot qayta boshlandi. Tilni tanlang:",
    },
}

LANG_BUTTONS = {
    "RUS 🇷🇺": "ru",
    "ENG 🇬🇧": "en",
    "UZB 🇺🇿": "uz",
    "QQ 🌐": "qq",
}

BUTTON_LABELS = {
    "ru": {
        "find": "🔎 Найти термин",
        "list": "📚 Список терминов",
        "history": "🕘 История",
        "lang": "🌐 Сменить язык",
        "help": "ℹ️ Помощь",
        "restart": "🔄 Перезапустить",
    },
    "en": {
        "find": "🔎 Find term",
        "list": "📚 Term list",
        "history": "🕘 History",
        "lang": "🌐 Change language",
        "help": "ℹ️ Help",
        "restart": "🔄 Restart",
    },
    "uz": {
        "find": "🔎 Atamani qidirish",
        "list": "📚 Atamalar ro‘yxati",
        "history": "🕘 Tarix",
        "lang": "🌐 Tilni almashtirish",
        "help": "ℹ️ Yordam",
        "restart": "🔄 Qayta boshlash",
    },
    "qq": {
        "find": "🔎 Atamanı izlew",
        "list": "📚 Atamalar dizimi",
        "history": "🕘 Tariyx",
        "lang": "🌐 Tildi ózgertiw",
        "help": "ℹ️ Járdem",
        "restart": "🔄 Qaytadan baslaw",
    },
}


def language_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="RUS 🇷🇺"), KeyboardButton(text="ENG 🇬🇧")],
            [KeyboardButton(text="UZB 🇺🇿"), KeyboardButton(text="QQ 🌐")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Tildi tańlań / Choose language",
    )


def main_keyboard(lang: str):
    labels = BUTTON_LABELS[lang]
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=labels["find"])],
            [KeyboardButton(text=labels["list"]), KeyboardButton(text=labels["history"])],
            [KeyboardButton(text=labels["lang"]), KeyboardButton(text=labels["help"])],
            [KeyboardButton(text=labels["restart"])],
        ],
        resize_keyboard=True,
        input_field_placeholder="Ekologiyalıq termindi kiritiń...",
    )


# ================== ПОИСК ==================
def normalize(text: str) -> str:
    text = text.strip().lower()
    text = " ".join(text.split())
    return text


def find_term(query: str):
    q = normalize(query)
    q_no_space = q.replace(" ", "")

    for term in terms:
        variants = [
            normalize(term.get("ru_term", "")),
            normalize(term.get("en_term", "")),
            normalize(term.get("uz_term", "")),
            normalize(term.get("qq_term", "")),
        ]

        variants_no_space = [v.replace(" ", "") for v in variants]

        if q in variants or q_no_space in variants_no_space:
            return term

    return None


def format_term(term: dict, lang: str) -> str:
    texts = LANG_TEXTS[lang]
    term_key = f"{lang}_term"
    def_key = f"{lang}_definition"

    return (
        f"{texts['term_label']} {term.get(term_key, '—')}\n\n"
        f"{texts['def_label']}\n{term.get(def_key, '—')}"
    )


def format_terms_list(lang: str) -> str:
    term_key = f"{lang}_term"
    lines = [f"📚 <b>{LANG_TEXTS[lang]['list']}</b>\n"]

    for i, term in enumerate(terms, start=1):
        lines.append(f"{i}. {term.get(term_key, '—')}")

    text = "\n".join(lines)

    # Telegram message limit protection
    if len(text) > 3900:
        text = text[:3900] + "\n\n..."
    return text


def format_history(user_id: int, lang: str) -> str:
    if not history[user_id]:
        return LANG_TEXTS[lang]["empty_history"]

    lines = [f"🕘 <b>{LANG_TEXTS[lang]['history']}</b>\n"]
    for i, item in enumerate(reversed(history[user_id]), start=1):
        lines.append(f"{i}. <code>{item}</code>")
    return "\n".join(lines)


# ================== HANDLERS ==================
@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        LANG_TEXTS["qq"]["welcome"],
        reply_markup=language_keyboard(),
    )


@dp.message(Command("restart"))
async def restart_command(message: Message):
    user_id = message.from_user.id
    user_lang.pop(user_id, None)
    history[user_id].clear()
    await message.answer(
        LANG_TEXTS["qq"]["restart"],
        reply_markup=language_keyboard(),
    )


@dp.message(F.text.in_(list(LANG_BUTTONS.keys())))
async def set_language(message: Message):
    user_id = message.from_user.id
    lang = LANG_BUTTONS[message.text]
    user_lang[user_id] = lang

    await message.answer(
        LANG_TEXTS[lang]["selected"],
        reply_markup=main_keyboard(lang),
    )


@dp.message(F.text)
async def text_handler(message: Message):
    user_id = message.from_user.id
    text = message.text.strip()
    lang = user_lang.get(user_id)

    if not lang:
        await message.answer(
            LANG_TEXTS["qq"]["choose"],
            reply_markup=language_keyboard(),
        )
        return

    labels = BUTTON_LABELS[lang]

    if text == labels["find"]:
        await message.answer(
            LANG_TEXTS[lang]["search"],
            reply_markup=main_keyboard(lang),
        )
        return

    if text == labels["list"]:
        await message.answer(
            format_terms_list(lang),
            reply_markup=main_keyboard(lang),
        )
        return

    if text == labels["history"]:
        await message.answer(
            format_history(user_id, lang),
            reply_markup=main_keyboard(lang),
        )
        return

    if text == labels["help"]:
        await message.answer(
            LANG_TEXTS[lang]["help"],
            reply_markup=main_keyboard(lang),
        )
        return

    if text == labels["lang"]:
        await message.answer(
            LANG_TEXTS["qq"]["welcome"],
            reply_markup=language_keyboard(),
        )
        return

    if text == labels["restart"]:
        user_lang.pop(user_id, None)
        history[user_id].clear()
        await message.answer(
            LANG_TEXTS["qq"]["restart"],
            reply_markup=language_keyboard(),
        )
        return

    result = find_term(text)

    if result:
        history[user_id].append(text)
        await message.answer(
            format_term(result, lang),
            reply_markup=main_keyboard(lang),
        )
    else:
        await message.answer(
            LANG_TEXTS[lang]["not_found"],
            reply_markup=main_keyboard(lang),
        )


# ================== WEB SERVER FOR RENDER ==================
async def handle(request):
    return web.Response(text="Bot is running!")


async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()


async def main():
    print("BOT ISKE TÚSTI")

    await start_web_server()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
