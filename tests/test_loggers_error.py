import unittest
from rigelcore.loggers import ErrorLogger
from rigelcore.exceptions import RigelError
from unittest.mock import Mock, patch


class ErrorLoggerTesting(unittest.TestCase):
    """
    Test suite for rigelcore.loggers.ErrorLogger class.
    """

    @patch('rigelcore.loggers.error.rich_print')
    def test_log_error_message(self, print_mock: Mock) -> None:
        """
        Ensure that error messages are displayed with the proper style.
        """

        msg_style = 'bold red'
        code_style = 'bold'

        err = RigelError()
        logger = ErrorLogger()
        logger.log(err)

        print_mock.assert_called_once_with(
            f'[{msg_style}]{err.base}[/{msg_style}] ([{code_style}]Error: {err.code}[/{code_style}])'
        )


if __name__ == '__main__':
    unittest.main()
