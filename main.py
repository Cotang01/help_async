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
                            help='URL of the currency exchange rate source')
        parser.add_argument('--sleep', default=3,
                            help='Interval in seconds for updating the currency exchange rate')
        parser.add_argument('--tracking_point', default=0.5,
                            help='Threshold for generating log messages when the currency rate changes')
        parser.add_argument('--headers', default={'User-Agent': 'Mozilla/5.0'},
                            help='HTTP headers for making requests to the currency source')
        parser.add_argument('--log_config',
                            default={"level": logging.INFO,
                                     "format": "%(asctime)s %(levelname)s %(message)s",
                                     "filename": "logger.log"},
                            help='Configuration parameters for logging')
        args = parser.parse_args()
        self.currency_source = args.currency_source
        self.sleep = int(args.sleep)
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

            full_page = await self.loop.run_in_executor(
                None, requests.get,
                self.currency_source,
                {'headers': self.headers})
            full_page.raise_for_status()
            soup = BeautifulSoup(full_page.content, 'html.parser')
            convert = soup.findAll("div", {"class": "valvalue"})
            return float(convert[0].text.replace(',', '.'))

        except requests.RequestException as rre:
            logger.error("Could not get answer from web-source")
            raise rre
        except ValueError as ve:
            logger.error("The obtained element is not a number")
            raise ve
        except IndexError as ie:
            logger.error("BeautifulSoup didn't find objects of class "
                         "'valvalue'")
            raise ie

    async def check_currency(self, logger):
        while self.start_flag:
            try:
                new_currency = await self.get_currency_price(logger)
                if new_currency is None:
                    raise ValueError("Gathered currency is None")
                if self.current_currency is None:
                    logger.warning("Start! Current currency value: %s",
                                   new_currency)
                elif new_currency > self.current_currency + self.tracking_point:
                    logger.warning(
                        "The course has grown a lot! Current currency value: %f",
                        new_currency)
                elif new_currency < self.current_currency - self.tracking_point:
                    logger.warning(
                        "The course has dropped a lot! Current currency value: %f",
                        new_currency)
                if self.current_currency != new_currency:
                    self.current_currency = new_currency
                logger.info(f'{new_currency}')
                await asyncio.sleep(self.sleep)
            except requests.RequestException as rre:
                logger.error("Could not connect to web-source")
                raise rre
            except ValueError as ve:
                logger.error("The result of currency price is None")
                raise ve
            except IndexError as ie:
                logger.error("Gathered data has no elements")
                raise ie
            except asyncio.CancelledError as ace:
                logger.warning("The sleep of check_currency() hasn't been "
                               "ended")
                raise ace


async def waiting_input():
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        input,
        'Enter command:\n'
        'Choose: Currency, Price, Exit\n')


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
    temp = None
    run = True
    while run:
        try:
            start = await waiting_input()
            if start == "Currency":
                if currency_gather.start_flag == 0:
                    currency_gather.start_flag += 1
                    temp = asyncio.gather(currency_gather.check_currency(logger))
                    logger.warning("Type 'Exit' if you see any errors")
                else:
                    logger.warning("The program has already started tracking currency exchange rates")
            elif start == 'Price':
                if currency_gather.start_flag != 1:
                    logger.warning("The program has not started tracking "
                                   "currency exchange rates")
                else:
                    logger.info(currency_gather.current_currency)
            elif start == 'Exit':
                currency_gather.start_flag = 0
                run = False
                if temp is not None:
                    # Force exit
                    # temp.cancel()
                    await temp
                logger.warning("The program has been stopped")
            else:
                logger.warning(
                    'There is no such command\n'
                    'List of commands:\n'
                    'Currency - launch currency rate tracking and logging\n'
                    'Price - current price value\n'
                    'Exit - exit')
        except requests.RequestException:
            logger.error("Error occurred when trying to connect to web-source")
        except ValueError:
            logger.error("The program couldn't to work with NoneType")
        except IndexError:
            logger.error("The program tried to reach nonexistent element")
        except asyncio.CancelledError:
            logger.warning("Last call was cancelled")


if __name__ == "__main__":
    asyncio.run(main())
