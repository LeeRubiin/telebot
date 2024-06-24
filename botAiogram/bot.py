import asyncio
from aiogram import Bot, Dispatcher
from handlers import questions

# Запуск бота
async def main():
    bot = Bot(token="7095289212:AAF-4TR25WYJSQlaSPgkpcBPwPimDylrQBs")
    dp = Dispatcher()
    dp.include_routers(questions.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())