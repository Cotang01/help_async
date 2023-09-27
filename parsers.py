import logging
import configargparse


class ParseIni:
    """
    A class for parsing configuration from an INI files.

    Attributes
    ----------
        currency_source : str
            URL of the currency exchange rate source.
        sleep : int
            Interval in seconds for updating the currency exchange rate.
        tracking_point : float
            Threshold for generating log messages when the currency rate changes.
        headers : str
            HTTP headers for making requests to the currency source.
        log_config : dict
            Configuration parameters for logging.
    """
    def __init__(self):
        """ Sets the attributes of the ParseIni object using config file. """
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

        # Assign the parsed values to the class attributes
        self.currency_source = args.currency_source
        self.sleep = int(args.sleep)
        self.tracking_point = float(args.tracking_point)
        self.headers = args.headers
        self.log_config = args.log_config
