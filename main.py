import asyncio
import requests
from bs4 import BeautifulSoup
import logging
import json
import sys
import configargparse


class ParseIni:
    def __init__(self):
        parser = configargparse.ArgParser()
        # TODO line 15 вернуть config.txt обратно в config.ini если нужно
        # config.ini на время дебага заменён на config.txt
        parser.add_argument('-c', '--config', default='config.txt',
                            is_config_file=True,
                            help='Путь к файлу config.ini')
        parser.add_argument('--currency_source',
                            default='http://www.finmarket.ru/currency/USD/',
                            help='Источник веб-страницы с курсом валюты')
        parser.add_argument('--sleep', default=3,
                            help='Задержка обновления в секундах')
        parser.add_argument('--tracking_point', default=0.5,
                            help='Точка изменения курса')
        parser.add_argument('--headers',
                            default=
                            {
                                'User-Agent': 'Mozilla/5.0'
                            },
                            help='Заголовки запроса')
        parser.add_argument('--log_config',
                            default=
                            {
                                "level": logging.INFO,
                                "format":
                                    "%(asctime)s %(levelname)s %(message)s",
                                "filename": "logger.log"
                            },
                            help='Конфигурация логирования')
        args = parser.parse_args()
        self.currency_source = args.currency_source
        self.sleep = args.sleep
        self.tracking_point = args.tracking_point
        self.headers = args.headers
        self.log_config = args.log_config


class Currency:

    def __init__(self, currency_source, headers, tracking_point, sleep):
        self.currency_source = currency_source
        self.headers = headers
        self.tracking_point = tracking_point
        self.loop = asyncio.get_event_loop()
        self.start_flag = 0
        self.starting_currency = None
        self.sleep = sleep

    async def get_currency_price(self):
        try:
            full_page = await self.loop.run_in_executor(
                None,
                requests.get,
                self.currency_source)
            soup = BeautifulSoup(full_page.content, 'html.parser')
            convert = soup.findAll("div", {"class": "valvalue"})
            return float(convert[0].text.replace(',', '.'))
        except ValueError as ve:
            return ve

    async def check_currency(self, logger):
        while self.start_flag:
            try:
                currency = await self.get_currency_price()
                if isinstance(currency, ValueError):
                    raise ValueError
                self.tracking_point = float(self.tracking_point)
                if self.starting_currency is None:
                    logger.warning("Старт! Текущая цена валюты: %f", currency)
                    self.starting_currency = currency
                if currency > self.starting_currency + self.tracking_point:
                    logger.warning(
                        "The course has grown a lot! "
                        "Current currency value: %f",
                        currency)
                else:
                    if currency < self.starting_currency - self.tracking_point:
                        logger.warning(
                            "The course has dropped a lot! "
                            "Current currency value: %f", currency)
                    self.starting_currency = currency
                    logger.info(f'{self.starting_currency}')
                await asyncio.sleep(float(self.sleep))
                # Интервал по дефолту 3 секунды
            except ValueError as ve:
                logger.error("Ошибка парсинга данных!")


async def waiting_input():
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, input, 'Введите команду:\n')


async def main():
    used_args = ParseIni()
    json_data = json.loads(used_args.log_config)
    logger = logging.getLogger("main")
    logger.setLevel(json_data['level'])
    handler = logging.FileHandler(f'{json_data["filename"]}', mode='a')
    formatter = logging.Formatter(json_data['format'])
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.WARNING)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    logger.info(used_args.log_config)
    current_currency = Currency(
        used_args.currency_source,
        used_args.headers,
        used_args.tracking_point,
        used_args.sleep
    )

    '''
    При логгировании будет использоваться .warning для той информации, которая
    должна выводиться в консоль
    '''
    
    logger.warning(
        'List of commands:\n'
        'Currency - launch currency rate tracking and logging\n'
        'Price - current price value\n'
        'Exit - exit')

    temp = None
    run = True
    while run:
        start = await waiting_input()
        match start:
            case "Currency":
                current_currency.start_flag = 1
                temp = asyncio.gather(current_currency.check_currency(logger))
            case 'Price':
                logger.warning(current_currency.starting_currency)
                try:
                    await temp
                except Exception as e:
                    logger.error('Logging has not been started: %s', e)
                break
            case 'Exit':
                current_currency.start_flag = 0
                logger.warning("The program has been shut down")
                run = False
            case _:
                logger.warning(
                    'There is no such command\n'
                    'List of commands:\n'
                    'Currency - launch currency rate tracking and logging\n'
                    'Price - current price value\nExit - exit'
                )


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
