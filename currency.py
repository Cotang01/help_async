import asyncio
import logging
import requests
from asyncio import Event
from bs4 import BeautifulSoup


class Currency:
    """
    A class for tracking currency exchange rates.

    Arguments
    ---------
        currency_source : str
            The source URL for getting currency prices.
        headers : dict
            The headers to be used in the HTTP request.
        tracking_point : float
            The threshold for tracking currency changes.
        sleep : int
            The time interval between currency checks.

    Attributes
    ----------
        currency_source : str
            The source URL for getting currency prices.
        headers : dict
            The headers to be used in the HTTP request.
        tracking_point : float
            The threshold for tracking currency changes.
        loop : AbstractEventLoop
            The event loop for running asynchronous tasks.
        current_currency : float
            The current currency price.
        sleep : int
            The time interval between currency checks.
        data_is_ready : Event
            Flag that will track if one iteration of currency checking is done.

    Methods
    -------
        get_currency_price():
            Fetches the current currency price from the source.
        check_currency(logger):
            Checks the currency price periodically and logs any changes.
    """
    def __init__(self, currency_source, headers, tracking_point, sleep):
        """
        Sets the attributes of the Currency class object using
        incoming parameters.

        :param currency_source: The source URL for getting currency prices.
        :type currency_source: str

        :param headers: The headers to be used in the HTTP request.
        :type headers: dict

        :param tracking_point: The threshold for tracking currency changes.
        :type tracking_point: float

        :param sleep: The time interval between currency checks.
        :type sleep: int
        """
        self.currency_source = currency_source
        self.headers = headers
        self.tracking_point = tracking_point
        self.loop = asyncio.get_event_loop()
        self.current_currency = None
        self.sleep = sleep
        self.data_is_ready = Event()

    async def get_currency_price(self) -> float:
        """
        Fetches the current currency price from the source.

        :return: The current currency price.
        :rtype: float

        :raises requests.RequestException:
            If there is an error in making the HTTP request.
        :raises ValueError:
            If the fetched element is of NoneType or there is an error in
            converting the price to float.
        :raises IndexError:
            If there is an error in accessing the fetched element.
        """
        try:

            full_page = await self.loop.run_in_executor(
                None, requests.get,
                self.currency_source,
                {'headers': self.headers})

            full_page.raise_for_status()
            soup = BeautifulSoup(full_page.content, 'html.parser')
            convert = soup.findAll('div', {'class': 'valvalue'})
            if convert is None:
                raise ValueError
            return float(convert[0].text.replace(',', '.'))

        except (requests.RequestException, ValueError,  IndexError):
            raise

    async def check_currency(self, logger: logging.Logger) -> None:
        """
        Checks the currency price periodically and logs any changes.

        :argument logger: Configured logger
        :type logger: logger.Logger

        :raises requests.RequestException, ValueError, IndexError:
            If it was raised by `get_currency_price`
        :raises asyncio.CancelledError:
            If the program was stopped by user's interaction
        """
        while True:
            try:
                new_currency = await self.get_currency_price()
                if self.current_currency is None:
                    logger.warning(
                        f'Start! Current currency value: {new_currency}')
                elif new_currency > self.current_currency + self.tracking_point:
                    logger.warning(
                        f'The course has grown a lot! Current currency '
                        f'value: {new_currency}')
                elif new_currency < self.current_currency - self.tracking_point:
                    logger.warning(
                        f'The course has dropped a lot! Current currency '
                        f'value: {new_currency}')
                if self.current_currency != new_currency:
                    self.current_currency = new_currency
                logger.info(f'Current exchange rates value: {new_currency}')
                if not self.data_is_ready.is_set():
                    self.data_is_ready.set()
            except (requests.RequestException, ValueError, IndexError):
                logger.error('Some errors occurred when trying to get '
                             'exchange rates... Solving the problem...')
            if not asyncio.current_task().cancelled():
                await asyncio.sleep(self.sleep)
