import asyncio
import requests
import json
from main_logger import log
from currency import Currency
from parsers import ParseIni
import aioconsole


async def waiting_input():
    """
    Waits for user's input.

    :return: Result of the user's input.
    :rtype: str
    """
    return await aioconsole.ainput('Enter command:\n'
                                   'Choose: Price, Exit\n')


async def main():
    """
    A main function that starts whole program.
    1) Parses configuration file.
    2) Creates logger.
    3) Gathers information of currency exchange rates and logs them.
    The program's behaviour depends on user's inputs.
    """
    used_args = ParseIni()
    json_data = json.loads(used_args.log_config)
    logger = log(used_args.log_config, json_data)

    currency_gather = Currency(used_args.currency_source,
                               used_args.headers,
                               used_args.tracking_point,
                               used_args.sleep)

    currency_gather.start_flag = 1
    temp = asyncio.gather(currency_gather.check_currency(logger))
    logger.warning("Type 'Exit' if you meet any errors")

    while True:
        if currency_gather.start_flag == 0:
            break
        try:
            start = await waiting_input()
            match start:
                case 'Price':
                    if currency_gather.start_flag == 0:
                        logger.warning("The exchange rates tracking has not "
                                       "been started")
                    else:
                        logger.info(f"Current exchange rates value: "
                                    f"{currency_gather.current_currency}")
                case 'Exit':
                    currency_gather.start_flag = 0
                    if temp is not None:
                        # Force exit
                        temp.cancel()
                        await temp
                case _:
                    logger.warning(
                        'There is no such command\n'
                        'List of commands:\n'
                        'Price - current price value\n'
                        'Exit - exit')

        except (requests.RequestException, ValueError, IndexError,
                asyncio.CancelledError):
            pass


if __name__ == "__main__":
    asyncio.run(main())
