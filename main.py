import asyncio
import requests
from logger import get_logger
from currency import Currency
from parsers import ParseIni
import aioconsole


async def main():
    """
    A main function that starts whole program.
    1) Parses configuration file.
    2) Creates logger.
    3) Gathers information of currency exchange rates and logs them.
    The program's behaviour depends on user's inputs.
    """
    used_args = ParseIni()
    logger = get_logger(used_args.log_config.get('level'),
                        used_args.log_config.get('format'),
                        used_args.log_config.get('filename'))

    currency_gather = Currency(used_args.currency_source,
                               used_args.headers,
                               used_args.tracking_point,
                               used_args.sleep)

    currency_tracking = asyncio.create_task(currency_gather.check_currency(logger))
    logger.warning('Starting tracking currency exchange rates, please wait...')
    await currency_gather.data_is_ready.wait()

    while True:
        try:
            start = await aioconsole.ainput('Enter command:\n'
                                            'Choose: Price, Exit\n')
            match start.lower():
                case 'price': logger.info(f'Current exchange rates value: '
                                          f'{currency_gather.current_currency}')
                case 'exit':
                    currency_tracking.cancel()
                    break
                case _:
                    logger.warning(
                        'There is no such command\n'
                        'List of commands:\n'
                        'Price - current price value\n'
                        'Exit - exit')
        except (requests.RequestException, ValueError, IndexError,
                asyncio.CancelledError):
            pass


if __name__ == '__main__':
    asyncio.run(main())
