import asyncio
from os import getenv
from logger import get_logger

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold

from parsers import ParseIni

TOKEN = getenv('TOKEN')

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()


async def on_startup(_):
    print('Бот запущен')  # Пишет в консоль
    await _.send_message(chat_id=767528224, text='Started!')


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    print('Started!')
    logger.warning('The bot has been started!')
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")


@dp.message()
async def echo_handler(message: types.Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types
    """
    try:
        # Send a copy of the received message
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    cfg = ParseIni().log_config
    logger = get_logger(cfg.get('level'),
                        cfg.get('format'),
                        cfg.get('filename'))
    # logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
