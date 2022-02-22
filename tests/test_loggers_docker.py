import unittest
from rigelcore.loggers import DockerLogPrinter
from unittest.mock import Mock, patch


class DockerLogPrinterTesting(unittest.TestCase):
    """
    Test suite for rigelcore.loggers.DockerLogPrinter class.
    """

    @patch('rigelcore.loggers.docker.rich_print')
    def test_print_stream_log(self, print_mock: Mock) -> None:
        """
        Ensure that 'stream' logs are displayed as expected.
        """

        test_stream_message = '     test_stream_message      '
        test_log = {'stream': test_stream_message}

        stream_style = 'bold magenta'

        logger = DockerLogPrinter()
        logger.log(test_log)

        print_mock.assert_called_once_with(
            f'[{stream_style}]stream\t|[/{stream_style}] {test_stream_message.strip()}'
        )

    @patch('rigelcore.loggers.docker.rich_print')
    def test_print_error_log(self, print_mock: Mock) -> None:
        """
        Ensure that 'error' logs are displayed as expected.
        """

        test_error_message = '     test_error_message      '
        test_log = {'error': test_error_message}

        stream_style = 'bold red'

        logger = DockerLogPrinter()
        logger.log(test_log)

        print_mock.assert_called_once_with(
            f'[{stream_style}]error\t|[/{stream_style}] {test_error_message.strip()}'
        )

    @patch('rigelcore.loggers.docker.rich_print')
    def test_unspecified_ifnored(self, print_mock: Mock) -> None:
        """
        Ensure that unspecified logs are ignored.
        """
        test_log = {'unknown': '     test_unknown_message      '}
        logger = DockerLogPrinter()
        logger.log(test_log)
        print_mock.assert_not_called()


if __name__ == '__main__':
    unittest.main()
