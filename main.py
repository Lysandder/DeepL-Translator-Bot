from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from aiogram.utils.markdown import hlink

import os

from flag import flag

import nest_asyncio
nest_asyncio.apply()

import deepl

DEEPL_KEY = ""  # Deepl API Key
translator = deepl.Translator(DEEPL_KEY)

TOKEN = ""  # Telegram Bot Token
bot = Bot(token = TOKEN)
dp = Dispatcher()


# /start
@dp.message(Command("start"))
async def start_command(message: Message):
    await message.delete()

    await message.answer(f"Привет {message.from_user.first_name}! Этот бот умеет переводить текста и документы.\n\
Для того, чтобы узнать о поддерживаемых языках и расширениях документов, используйте команду /help.\n\
Для того, чтобы выбрать язык на который вы будете переводить, используйте команду /lang.\n\
(Все команды доступны в меню.)")


# /help
@dp.message(Command("help"))
async def help_command(message: Message):
    await message.delete()

    lang_list_linked_text = hlink(title="Узнать подробнее", url="https://telegra.ph/Informaciya-o-dostupnyh-yazykah-02-07")  # f"<a href={url}>{text}</a>"    url: str, text: str
    formality_list_linked_text = hlink(title="Узнать подробнее", url="https://telegra.ph/O-funkcii-vybora-formalnosti-02-10")

    await message.answer(f"Этот бот может перевести текста, а так же документы в следующих форматах:\n\
- Word (.docx)\n\
- PowerPoint (.pptx)\n\
- Excel (.xlsx)\n\
- PDF (.pdf)\n\
- Text (.txt)\n\
\
На данный момент переводчик поддерживает 30 языков.\n\
{lang_list_linked_text}\n\n\
\
Некоторые языки поддерживают функцию выбора уровня формальности перевода.\n\
{formality_list_linked_text}\n\n\
\
Для того, чтобы выбрать язык на который вы будете переводить используйте команду /lang.\n\
(Все команды доступны в меню.)", parse_mode="HTML", disable_web_page_preview=True)


# Словарь со всеми флагми, языками и их DeepL кодами.
lang_dict = {
    1:  [flag("US"), "Английский (Американский)", "EN-US"],
    2:  [flag("GB"), "Английский (Британский)", "EN-GB"],
    3:  [flag("AR"), "Современный Стандартный Арабский (Только текст)", "AR"],
    4:  [flag("BG"), "Болгарский", "BG"],
    5:  [flag("HU"), "Венгерский", "HU"],
    6:  [flag("NL"), "Голландский", "NL"],
    7:  [flag("GR"), "Греческий", "EL"],
    8:  [flag("NL"), "Датский", "DA"],
    9:  [flag("ID"), "Индонезийский", "ID"],
    10: [flag("ES"), "Испанский", "ES"],
    11: [flag("IT"), "Итальянский", "IT"],
    12: [flag("CN"), "Китайский (Упрощенный)", "ZH"],
    13: [flag("KR"), "Корейский", "KO"],
    14: [flag("LV"), "Латышский", "LV"],
    15: [flag("LT"), "Литовский", "LT"],
    16: [flag("DE"), "Немецкий", "DE"],
    17: [flag("NO"), "Норвежский (Букмол)", "NB"],
    18: [flag("PL"), "Польский", "PL"],
    19: [flag("PT"), "Португальский (Бразильский)", "PT-BR"],
    20: [flag("PT"), "Португальский (Все кроме Бразильского)", "PT-PT"],
    21: [flag("RO"), "Румынский", "RO"],
    22: [flag("RU"), "Русский", "RU"],
    23: [flag("SK"), "Словацкий", "SK"],
    24: [flag("SL"), "Словенский", "SL"],
    25: [flag("TR"), "Турецкий", "TR"],
    26: [flag("UA"), "Украинский", "UK"],
    27: [flag("FI"), "Финский", "FI"],
    28: [flag("FR"), "Французский", "FR"],
    29: [flag("CZ"), "Чешский", "CS"],
    30: [flag("SV"), "Шведский", "SV"],
    31: [flag("ET"), "Эстонский", "ET"],
    32: [flag("JP"), "Японский", "JA"],
}

inline_keyboard_buttons = []
for i in range(1, 33):
    inline_keyboard_buttons.append([types.InlineKeyboardButton(text=lang_dict[i][0] + " " + lang_dict[i][1], callback_data=lang_dict[i][2])])


# /lang
@dp.message(Command("lang"))
async def language_command(message: Message):
    await message.delete()

    keyboard_markup = types.InlineKeyboardMarkup(inline_keyboard = inline_keyboard_buttons)
    await message.answer("Выберите язык на который вы будете переводить текста и файлы. (Вы также сможете изменить его позже)", reply_markup = keyboard_markup)


# Словарь с выбранными якыками пользователей, базы данных нет.
target_lang_dict = {}  # User: Language


# Получение результата из Инлайн Кнопок
@dp.callback_query()
async def lang_callback_query(callback: types.CallbackQuery):
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)
    target_lang_dict[callback.message.chat.id] = callback.data

    for key, value in lang_dict.items():
        if callback.data in value:
            chosen_lang_name = lang_dict[key][1]
            break

    await bot.send_message(callback.message.chat.id, text = f"Вы выбрали {chosen_lang_name} язык.\n\
Теперь любой отправленный текст или документ, \
написанный на поддерживаемом языке и с поддерживаемым расширением (подробнее - /help), будет переводиться на {chosen_lang_name} язык.\n\
Для того, чтобы поменять язык перевода, используйте /lang.\n\
(Все команды доступны в меню.)")


# Перевод текста
@dp.message(lambda message: message.text)
async def translate_text(message = types.Message):
    try:
        translated_text = str(translator.translate_text(message.text, target_lang=target_lang_dict[message.chat.id]))
        await message.reply(translated_text)

    except KeyError:
        await message.reply("ВНИМАНИЕ! Вы не выбрали язык перевода. Используйте команду /lang.")

    except:
        await message.reply("Ошибка")


# Перевод документов
@dp.message(lambda message: message.document)
async def translate_document(message = types.Message):
    file_path = (await bot.get_file(message.document.file_id)).file_path
    await bot.download_file(file_path, message.document.file_name)
    new_file_name = f"Translated {message.document.file_name}"

    try:
        with open(message.document.file_name, "rb") as in_file, open(new_file_name, "wb") as out_file:
            translator.translate_document(in_file, out_file, target_lang=target_lang_dict[message.chat.id])

        await message.reply_document(FSInputFile(new_file_name, filename=new_file_name))

    except KeyError:
        await message.reply("ВНИМАНИЕ! Вы не выбрали язык перевода. Используйте команду /lang.")

    except:
        await message.reply("Ошибка")
    
    os.remove(message.document.file_name)
    os.remove(new_file_name)

if __name__ == "__main__":
    dp.run_polling(bot)
