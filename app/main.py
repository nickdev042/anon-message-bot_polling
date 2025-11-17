import logging
import asyncio
import redis.asyncio as aioredis
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram.types import BotCommand, BotCommandScopeDefault
from handlers import router
from database.models import async_main
from config_reader import config

logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=config.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запустить бота 🚀"),
        BotCommand(command="report", description="Жалоба 🚫"),
        BotCommand(command="profile", description="Моя ссылка 👤"),
    ]
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())


async def main():
    redis = await aioredis.from_url("redis://172.28.215.180:6379/0")
    dp = Dispatcher(
        storage=RedisStorage(redis, key_builder=DefaultKeyBuilder(with_destiny=True))
    )
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)
    dp.include_router(router)
    await dp.start_polling(bot)


async def startup(bot: Bot):
    print("starting....")
    await set_bot_commands(bot)
    await async_main()


async def shutdown():
    print("shutting down....")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("error shutting down!!!!")
