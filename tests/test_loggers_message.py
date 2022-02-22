import unittest
from rigelcore.loggers import MessageLogger
from unittest.mock import Mock, patch


class MessageLoggerTesting(unittest.TestCase):
    """
    Test suite for rigelcore.loggers.MessageLogger class.
    """

    @patch('rigelcore.loggers.message.rich_print')
    def test_log_error_message(self, print_mock: Mock) -> None:
        """
        Ensure that error messages are displayed with the proper style.
        """
        style = 'bold red'
        test_error_message = 'Test error message.'

        logger = MessageLogger()
        logger.error(test_error_message)

        print_mock.assert_called_once_with(f'[{style}]ERROR - {test_error_message}[/{style}]')

    @patch('rigelcore.loggers.message.rich_print')
    def test_log_warning_message(self, print_mock: Mock) -> None:
        """
        Ensure that warning messages are displayed with the proper style.
        """
        style = 'bold yellow'
        test_error_message = 'Test warning message.'

        logger = MessageLogger()
        logger.warning(test_error_message)

        print_mock.assert_called_once_with(f'[{style}]WARNING - {test_error_message}[/{style}]')

    @patch('rigelcore.loggers.message.rich_print')
    def test_log_info_message(self, print_mock: Mock) -> None:
        """
        Ensure that info messages are displayed with the proper style.
        """
        style = 'bold green'
        test_error_message = 'Test info message.'

        logger = MessageLogger()
        logger.info(test_error_message)

        print_mock.assert_called_once_with(f'[{style}]{test_error_message}[/{style}]')


if __name__ == '__main__':
    unittest.main()
