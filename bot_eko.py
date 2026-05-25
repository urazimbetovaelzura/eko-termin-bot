import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Хранение выбранного языка пользователя
user_lang = {}

# База терминов
terms = [
    {
        "ru_term": "экология",
        "en_term": "ecology",
        "uz_term": "ekologiya",
        "qq_term": "ekologiya",
        "ru_def": "Наука о взаимодействии организмов с окружающей средой.",
        "en_def": "Science of interactions between organisms and the environment.",
        "uz_def": "Organizmlar va atrof-muhit o‘rtasidagi o‘zaro ta’sirni o‘rganuvchi fan.",
        "qq_def": "Organizmler menen qorshaǵan ortalıq arasındaǵı ózara tásirdi úyrenetuǵın pán.",
    },
    {
        "ru_term": "биосфера",
        "en_term": "biosphere",
        "uz_term": "biosfera",
        "qq_term": "biosfera",
        "ru_def": "Оболочка Земли, заселённая живыми организмами.",
        "en_def": "The Earth's shell inhabited by living organisms.",
        "uz_def": "Yerning tirik organizmlar yashaydigan qatlami.",
        "qq_def": "Jerdiń tiri organizmler jasaytuǵın qabatı.",
    },
    {
        "ru_term": "экосистема",
        "en_term": "ecosystem",
        "uz_term": "ekotizim",
        "qq_term": "ekosistema",
        "ru_def": "Совокупность живых организмов и среды их обитания.",
        "en_def": "A community of living organisms and their environment.",
        "uz_def": "Tirik organizmlar va ularning yashash muhiti majmui.",
        "qq_def": "Tiri organizmler hám olar jasaytuǵın ortalıq jıyındısı.",
    },
    {
        "ru_term": "загрязнение",
        "en_term": "pollution",
        "uz_term": "ifloslanish",
        "qq_term": "pataslanıw",
        "ru_def": "Негативное изменение окружающей среды под воздействием человека.",
        "en_def": "A harmful change in the environment caused by human activity.",
        "uz_def": "Atrof-muhitning inson faoliyati natijasida salbiy o‘zgarishi.",
        "qq_def": "Adam iskerligi nátiyjesinde qorshaǵan ortalıqtıń keri ózgerisi.",
    },
    {
        "ru_term": "климат",
        "en_term": "climate",
        "uz_term": "iqlim",
        "qq_term": "klimat",
        "ru_def": "Многолетний режим погоды на определённой территории.",
        "en_def": "The long-term pattern of weather in a particular area.",
        "uz_def": "Muayyan hududdagi ko‘p yillik ob-havo rejimi.",
        "qq_def": "Belgili bir aymaqtaǵı uzaq múddetli hawa rayı rejimi.",
    },
]

# Клавиатура выбора языка
lang_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="RUS 🇷🇺"), KeyboardButton(text="ENG 🇬🇧")],
        [KeyboardButton(text="UZB 🇺🇿"), KeyboardButton(text="QQ 🌐")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Tildi tańlań / Choose language",
)

# Основная клавиатура
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔎 Termindi tabıw")],
        [KeyboardButton(text="📚 Terminler dizimi"), KeyboardButton(text="🌐 Tildi ózgertiw")],
        [KeyboardButton(text="ℹ️ Járdem")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Ekologiyalıq termindi kiritiń...",
)

LANG_TEXTS = {
    "qq": {
        "welcome": "🌿 <b>Ekologiyalıq atamalar maǵlıwmatnamasına xosh kelipsiz!</b>\n\nInterfeys tilin saylań:",
        "lang_selected": "✅ Til saylandı: <b>Qaraqalpaq</b>\n\nEndi ekologiyalıq atamanı kirgiziń.",
        "search_prompt": "🔎 Ekologiyalıq atamanı kirgiziń.",
        "help": (
            "ℹ️ <b>Botтан paydalanıw tártibi:</b>\n\n"
            "1. Interfeys tilin tańlań.\n"
            "2. Atamanı rus, ingliz, ózbek yamasa qaraqalpaq tilinde kirgiziń.\n"
            "3. Bot atamanı tawıp, saylanǵan tilde anıqlamasın kórsetedi.\n\n"
            "Menyu túymeleri:\n"
            "🔎 Atamanı izlew\n"
            "📚 Atamalar dizimi\n"
            "🌐 Tildi ózgertiw"
        ),
        "term_list_title": "📚 <b>Bar atamalar:</b>\n\n",
        "term_label": "🌿 <b>Atama:</b>\n",
        "def_label": "📘 <b>Anıqlama:</b>\n",
        "not_found": "❌ <b>Atama tabılmadı.</b>\n\nJazılıwın tekseriń yamasa atamalar dizimin ashıń.",
        "choose_lang": "🌐 Aldın tildi saylań.",
    },
    "ru": {
        "welcome": "🌿 <b>Добро пожаловать в справочник экологических терминов!</b>\n\nВыберите язык интерфейса:",
        "lang_selected": "✅ Язык выбран: <b>Русский</b>\n\nТеперь введите экологический термин.",
        "search_prompt": "🔎 Введите экологический термин.",
        "help": (
            "ℹ️ <b>Как пользоваться ботом:</b>\n\n"
            "1. Выберите язык интерфейса.\n"
            "2. Введите термин на русском, английском, узбекском или каракалпакском языке.\n"
            "3. Бот найдёт термин и покажет определение на выбранном языке.\n\n"
            "Доступные команды меню:\n"
            "🔎 Найти термин\n"
            "📚 Список терминов\n"
            "🌐 Сменить язык"
        ),
        "term_list_title": "📚 <b>Доступные термины:</b>\n\n",
        "term_label": "🌿 <b>Термин:</b>\n",
        "def_label": "📘 <b>Определение:</b>\n",
        "not_found": "❌ <b>Термин не найден.</b>\n\nПроверьте написание или откройте список терминов.",
        "choose_lang": "🌐 Пожалуйста, сначала выберите язык.",
    },
    "en": {
        "welcome": "🌿 <b>Welcome to the ecological terms directory!</b>\n\nChoose the interface language:",
        "lang_selected": "✅ Language selected: <b>English</b>\n\nNow enter an ecological term.",
        "search_prompt": "🔎 Enter an ecological term.",
        "help": (
            "ℹ️ <b>How to use the bot:</b>\n\n"
            "1. Choose the interface language.\n"
            "2. Enter a term in Russian, English, Uzbek or Karakalpak.\n"
            "3. The bot will find the term and show the definition in the selected language.\n\n"
            "Available menu buttons:\n"
            "🔎 Find term\n"
            "📚 Term list\n"
            "🌐 Change language"
        ),
        "term_list_title": "📚 <b>Available terms:</b>\n\n",
        "term_label": "🌿 <b>Term:</b>\n",
        "def_label": "📘 <b>Definition:</b>\n",
        "not_found": "❌ <b>Term not found.</b>\n\nCheck the spelling or open the term list.",
        "choose_lang": "🌐 Please choose a language first.",
    },
    "uz": {
        "welcome": "🌿 <b>Ekologik atamalar ma'lumotnomasiga xush kelibsiz!</b>\n\nInterfeys tilini tanlang:",
        "lang_selected": "✅ Til tanlandi: <b>O‘zbek</b>\n\nEndi ekologik atamani kiriting.",
        "search_prompt": "🔎 Ekologik atamani kiriting.",
        "help": (
            "ℹ️ <b>Botdan foydalanish tartibi:</b>\n\n"
            "1. Interfeys tilini tanlang.\n"
            "2. Atamani rus, ingliz, o‘zbek yoki qoraqalpoq tilida kiriting.\n"
            "3. Bot atamani topib, tanlangan tilda ta’rifini ko‘rsatadi.\n\n"
            "Menyu tugmalari:\n"
            "🔎 Atamani qidirish\n"
            "📚 Atamalar ro‘yxati\n"
            "🌐 Tilni almashtirish"
        ),
        "term_list_title": "📚 <b>Mavjud atamalar:</b>\n\n",
        "term_label": "🌿 <b>Atama:</b>\n",
        "def_label": "📘 <b>Ta’rif:</b>\n",
        "not_found": "❌ <b>Atama topilmadi.</b>\n\nImlo tekshiring yoki atamalar ro‘yxatini oching.",
        "choose_lang": "🌐 Avval tilni tanlang.",
    },
}

BUTTON_LABELS = {
    "ru": {"find": "🔎 Найти термин", "list": "📚 Список терминов", "lang": "🌐 Сменить язык", "help": "ℹ️ Помощь"},
    "en": {"find": "🔎 Find term", "list": "📚 Term list", "lang": "🌐 Change language", "help": "ℹ️ Help"},
    "uz": {"find": "🔎 Atamani qidirish", "list": "📚 Atamalar ro‘yxati", "lang": "🌐 Tilni almashtirish", "help": "ℹ️ Yordam"},
    "qq": {"find": "🔎 Atamanı izlew", "list": "📚 Atamalar dizimi", "lang": "🌐 Tildi ózgertiw", "help": "ℹ️ Járdem"},
}

def get_lang(user_id: int) -> str:
    return user_lang.get(user_id, "ru")

def get_main_keyboard(lang: str) -> ReplyKeyboardMarkup:
    labels = BUTTON_LABELS[lang]
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=labels["find"])],
            [KeyboardButton(text=labels["list"]), KeyboardButton(text=labels["lang"])],
            [KeyboardButton(text=labels["help"])],
        ],
        resize_keyboard=True,
        input_field_placeholder="Введите термин..." if lang == "ru" else "Enter term...",
    )

def normalize(text: str) -> str:
    return " ".join(text.strip().lower().split())

def find_term(query: str):
    text = normalize(query)
    for term in terms:
        variants = [
            normalize(term["ru_term"]),
            normalize(term["en_term"]),
            normalize(term["uz_term"]),
            normalize(term["qq_term"]),
        ]
        if text in variants:
            return term
    return None

def format_term_single_lang(term: dict, lang: str, texts: dict) -> str:
    term_key = f"{lang}_term"
    def_key = f"{lang}_def"
    return (
        f"{texts['term_label']}{term[term_key]}\n\n"
        f"{texts['def_label']}{term[def_key]}"
    )

def format_term_list(lang: str, texts: dict) -> str:
    lines = [texts["term_list_title"]]
    for i, term in enumerate(terms, start=1):
        lines.append(f"<b>{i}.</b> {term[f'{lang}_term']}")
    return "\n".join(lines)

@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        LANG_TEXTS["qq"]["welcome"],
        parse_mode="HTML",
        reply_markup=lang_keyboard,
    )

@dp.message(F.text.in_(["RUS 🇷🇺", "ENG 🇬🇧", "UZB 🇺🇿", "QQ 🌐"]))
async def set_language_handler(message: Message):
    selected = message.text

    if selected == "RUS 🇷🇺":
        lang = "ru"
    elif selected == "ENG 🇬🇧":
        lang = "en"
    elif selected == "UZB 🇺🇿":
        lang = "uz"
    else:
        lang = "qq"

    user_lang[message.from_user.id] = lang
    texts = LANG_TEXTS[lang]

    await message.answer(
        texts["lang_selected"],
        parse_mode="HTML",
        reply_markup=get_main_keyboard(lang),
    )

@dp.message(F.text)
async def text_handler(message: Message):
    user_id = message.from_user.id
    text = message.text
    lang = user_lang.get(user_id)

    if not lang:
        await message.answer(
            LANG_TEXTS["ru"]["choose_lang"],
            parse_mode="HTML",
            reply_markup=lang_keyboard,
        )
        return

    texts = LANG_TEXTS[lang]
    labels = BUTTON_LABELS[lang]

    if text == labels["find"]:
        await message.answer(
            texts["search_prompt"],
            parse_mode="HTML",
            reply_markup=get_main_keyboard(lang),
        )
        return

    if text == labels["list"]:
        await message.answer(
            format_term_list(lang, texts),
            parse_mode="HTML",
            reply_markup=get_main_keyboard(lang),
        )
        return

    if text == labels["lang"]:
        await message.answer(
            "🌐 Tildi tańlań / Choose language:",
            reply_markup=lang_keyboard,
        )
        return

    if text == labels["help"]:
        await message.answer(
            texts["help"],
            parse_mode="HTML",
            reply_markup=get_main_keyboard(lang),
        )
        return

    result = find_term(text)

    if result:
        await message.answer(
            format_term_single_lang(result, lang, texts),
            parse_mode="HTML",
            reply_markup=get_main_keyboard(lang),
        )
    else:
        await message.answer(
            texts["not_found"],
            parse_mode="HTML",
            reply_markup=get_main_keyboard(lang),
        )

async def main():
    print("BOT ISKE TÚSTI")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
