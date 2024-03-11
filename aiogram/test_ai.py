

import asyncio
from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer


class TgSetting():
    chat_id = '1365913221'
    token = '6635610575:AAElSJZ3-2pSShXyx6PxHMQCMbca-Hhdd_c'


session = AiohttpSession(
    api=TelegramAPIServer.from_base('http://127.0.0.1:5000')
)


bot = Bot(
    token=TgSetting().token,
    session=session,
)


async def send_message(channel_id: int, text: str):
    await bot.send_message(channel_id, text)


async def main():
    await send_message(TgSetting().chat_id, '<b>Hello!</b>')


if __name__ == '__main__':
    asyncio.run(main())
