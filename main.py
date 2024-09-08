from aiogram import Bot, Dispatcher
import asyncio
from core.settings import get_settings

from core.handlers.basic import router as basic_router
from core.handlers.create_questionFSM import router as create_question_router
from core.handlers.complaintFSM import router as complaint_router
from core.handlers.complaintFSMcommands import router as complaint_commands_router

async def start():
    
    settings = get_settings('.env')

    bot = Bot(token=settings.bots.bot_token)
    dp = Dispatcher()

    dp.include_router(basic_router)
    dp.include_router(create_question_router)
    dp.include_router(complaint_router)
    dp.include_router(complaint_commands_router)

    try:
        await dp.start_polling(bot)
    finally:
        bot.session.close()

if __name__ == '__main__':
    asyncio.run(start())