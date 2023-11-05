import asyncio
import configargparse
from logger import get_logger
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    print('Started!')
    logger.warning('The bot has been started!')
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")


@dp.message()
async def echo_handler(message: types.Message) -> None:
    if message.text == '1+1':
        await message.answer('3')
    else:
        await message.answer('Nope, say 1+1')


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == '__main__':
    parser = configargparse.ArgParser()
    parser.add_argument('--log-level', env_var='LOG_LEVEL', required=True,
                        help='Log messages level')
    parser.add_argument('--log-format', env_var='LOG_FORMAT', required=True,
                        help='Log messages format')
    parser.add_argument('--log-file', env_var='LOG_FILE', required=True,
                        help='Log file name')
    parser.add_argument('--token', env_var='TOKEN', required=True,
                        help='Bot token')
    config = parser.parse_args()

    logger = get_logger(config.log_level,
                        config.log_format,
                        config.log_file)

    bot = Bot(config.token, parse_mode=ParseMode.HTML)
    asyncio.run(main())
