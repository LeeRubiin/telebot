from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_yes_no_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Казахский язык/Қазақ тілі")
    kb.button(text="Руский язык/Орыс тілі")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

def get_register_kb(language: str) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    if language == "kazakh":
        kb.button(text="Тіркелу")
    else:
        kb.button(text="Зарегистрироваться")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)
