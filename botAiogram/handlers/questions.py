from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from botAiogram.keyboards.for_questions import get_yes_no_kb, get_register_kb

router = Router()
user_languages = {}

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Сізді онлайн қазақ тілін үйренуге арналған бот қарсы алады! Жұмыс жасауға ыңғайлы тілді таңдаңыз \nВас приветствует бот для изучения казахского языка онлайн! Выберите язык, с которым вам удобно работать",
        reply_markup=get_yes_no_kb()
    )

@router.message(F.text.casefold() == "казахский язык/қазақ тілі")
async def answer_yes(message: Message):
    user_languages[message.from_user.id] = "kazakh"
    await message.answer(
        "Таңдалған тіл сақталды. Оқу бастамас бұрын тіркелуіңізді сұраймыз.",
        reply_markup=get_register_kb("kazakh")
    )

@router.message(F.text.casefold() == "руский язык/орыс тілі")
async def answer_no(message: Message):
    user_languages[message.from_user.id] = "russian"
    await message.answer(
        "Выбранный язык сохранен. Прежде чем начать обучение, пожалуйста, пройдите регистрацию.",
        reply_markup=get_register_kb("russian")
    )

@router.message(F.text.casefold() == "зарегистрироваться" or F.text.casefold() == "тіркелу")
async def register(message: Message):
    user_language = user_languages.get(message.from_user.id, "russian")
    if user_language == "kazakh":
        await message.answer(
            "Сіз тіркелдіңіз. Қазақ тілін үйренуді бастауға болады!",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message.answer(
            "Вы зарегистрированы. Можете начать изучение казахского языка!",
            reply_markup=ReplyKeyboardRemove()
        )
