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
        parser.add_argument('-c, --config', default='config.ini',
                            is_config_file=True,
                            help='Path to file config.ini')
        parser.add_argument('--currency_source',
                            default='http://www.finmarket.ru/currency/USD/',
                            help='Currency web-source')
        parser.add_argument('--sleep', default=3,
                            help='Update delay in seconds')
        parser.add_argument('--tracking_point', default=0.5,
                            help='Change rate point')
        parser.add_argument('--headers', default={'User-Agent': 'Mozilla/5.0'},
                            help='Browser information')
        parser.add_argument('--log_config',
                            default={"level": logging.INFO,
                                     "format": "%(asctime)s %(levelname)s %(message)s",
                                     "filename": "logger.log"},
                            help='Logging format')
        args = parser.parse_args()
        self.currency_source = args.currency_source
        self.sleep = args.sleep
        self.tracking_point = float(args.tracking_point)
        self.headers = args.headers
        self.log_config = args.log_config


class Currency:

    def __init__(self, currency_source, headers, tracking_point, sleep):
        self.currency_source = currency_source
        self.headers = headers
        self.tracking_point = tracking_point
        self.loop = asyncio.get_event_loop()
        self.start_flag = 0
        self.current_currency = None
        self.sleep = sleep

    async def get_currency_price(self, logger):
        try:
            full_page = await self.loop.run_in_executor(None, requests.get,
                                                        self.currency_source, {
                                                            'headers': self.headers})
            full_page.raise_for_status()

            soup = BeautifulSoup(full_page.content, 'html.parser')
            convert = soup.findAll("div", {"class": "value"})
            try:
                if not convert:
                    raise ValueError
            except (requests.RequestException, ValueError) as ve:
                logger.error("BeautifulSoup could not find an exchange "
                             "rates!")
                raise ve
            try:
                return float(convert[0].text.replace(',', '.'))
            except AttributeError as ae:
                logger.error("Exchange rates gotten by BeautifulSoup are "
                             "inappropriate!")
                raise ae
        except (requests.RequestException, ValueError, AttributeError):
            logger.error("Error when getting exchange rates!")

    async def check_currency(self, logger):
        while self.start_flag:
            try:
                new_currency = await self.get_currency_price(logger)
                if new_currency is None:
                    raise ValueError
                if self.current_currency is None:
                    logger.warning("Start! Current currency value: %f",
                                   new_currency)
                    self.current_currency = new_currency
                elif new_currency > self.current_currency + self.tracking_point:
                    logger.warning(
                        "The course has grown a lot! Current currency value: %f",
                        new_currency)
                    self.current_currency = new_currency
                elif new_currency < self.current_currency - self.tracking_point:
                    logger.warning(
                        "The course has dropped a lot! Current currency value: %f",
                        new_currency)
                    self.current_currency = new_currency
                logger.info(f'{new_currency}')
                await asyncio.sleep(self.sleep)
            except (requests.RequestException, ValueError):
                logger.error("Could not get currency from the source!")
                break


async def waiting_input():
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, input, 'Enter command:\n')


async def main():
    used_args = ParseIni()
    json_data = json.loads(used_args.log_config)
    logger = logging.getLogger(__name__)
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
    currency_gather = Currency(used_args.currency_source,
                               used_args.headers, used_args.tracking_point,
                               used_args.sleep)
    start = None
    temp = None
    while True:
        if start == "Currency":
            currency_gather.start_flag = 1
            temp = asyncio.gather(currency_gather.check_currency(logger))
        elif start == 'Price':
            logger.info(currency_gather.current_currency)
        elif start == 'Exit':
            currency_gather.start_flag = 0
            try:
                await temp
            except Exception as e:
                logger.error('Logging has not started: %s', e)
            break
        elif start:
            pass
        else:
            logger.warning(
                'There is no such command\nList of commands:\nCurrency - launch currency rate tracking and logging'
                '\nPrice - current price value\nExit - exit')
        start = await waiting_input()


if __name__ == "__main__":
    asyncio.run(main())
