import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from handlers import rt
from config import TG_TOKEN, cmds_list
from db import check_db_connection, init_db

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,  # Уровень логирования (INFO, DEBUG, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Формат сообщений
    handlers=[
        logging.FileHandler("bot.log"),  # Логи в файл
        logging.StreamHandler()  # Логи в консоль
    ]
)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = Bot(token=TG_TOKEN)

# Инициализация диспетчера
dp = Dispatcher()

# Подключение роутера
dp.include_router(rt)

async def main():
    try:
        logger.info("Проверка подключения к базе данных...")
        await check_db_connection()
        logger.info("Подключение к базе данных успешно.")

        logger.info("Инициализация базы данных...")
        init_db()
        logger.info("База данных инициализирована.")

        logger.info("Удаление вебхука...")
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Вебхук удален.")

        logger.info("Установка команд бота...")
        await bot.set_my_commands(
            commands=cmds_list,
            scope=types.BotCommandScopeAllPrivateChats()
        )
        logger.info("Команды бота установлены.")

        logger.info("Запуск бота...")
        await dp.start_polling(bot)
        logger.info("Бот запущен и работает.")
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        raise

if __name__ == '__main__':
    logger.info("Начинаю работать")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен вручную.")
    except Exception as e:
        logger.error(f"Ошибка в основном цикле: {e}")





# import asyncio
# from aiogram import Bot, Dispatcher, types
# from aiogram.fsm.strategy import FSMStrategy
# from handlers import rt
# from config import TG_TOKEN, cmds_list
# from db import check_db_connection, init_db
# import logging
#
# bot = Bot(token=TG_TOKEN)
#
# dp = Dispatcher()
#
# dp.include_router(rt)
#
#
# async def main():
#     await check_db_connection()
#     init_db()
#     await bot.delete_webhook(drop_pending_updates=True)
#     await bot.set_my_commands(
#         commands=cmds_list,
#         scope=types.BotCommandScopeAllPrivateChats()
#     )
#     await dp.start_polling(bot, allowed_updates=['message'])
#
#
# if __name__ == '__main__':
#     print('Начинаю работать')
#     asyncio.run(main())
