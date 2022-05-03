from hpl.ast import HplBinaryOperator, HplFieldAccess, HplLiteral
from typing import Any, Dict, Callable, Union

ROSMessageValue = Any
ROSMessageType = Dict[str, Any]
ROSCallbackType = Callable[[ROSMessageType], bool]


class CallbackGenerator:

    def generate_callback_equal(self, field: str, value: ROSMessageValue) -> ROSCallbackType:
        """
        Generate a base callback function that verifies
        if a ROS message field equals a certain reference value.

        :param field: The ROS message field.
        :type field: Any
        :param value: The reference value.
        :type value: Any
        :rtype: Callable[[Dict[str, Any]], bool]
        :return: A function that returns True if the ROS message field and the reference value are equal.
        False otherwise.
        """
        def callback(msg: ROSMessageType) -> bool:
            return bool(msg[field] == value)
        return callback

    def generate_callback_different(self, field: str, value: ROSMessageValue) -> ROSCallbackType:
        """
        Generate a base callback function that verifies
        if a given ROS message field is different from a certain reference value.

        :param field: The ROS message field.
        :type field: Any
        :param value: The reference value.
        :type value: Any
        :rtype: Callable[[Dict[str, Any]], bool]
        :return: A function that returns True if the ROS message field is different from the reference value.
        False otherwise.
        """
        def callback(msg: ROSMessageType) -> bool:
            return bool(msg[field] != value)
        return callback

    def generate_callback_lesser(self, field: str, value: ROSMessageValue) -> ROSCallbackType:
        """
        Generate a base callback function that verifies
        if a given ROS message field is lesser than a certain reference value.

        :param field: The ROS message field.
        :type field: Any
        :param value: The reference value.
        :type value: Any
        :rtype: Callable[[Dict[str, Any]], bool]
        :return: A function that returns True if the ROS message field is lesser than the reference value.
        False otherwise.
        """
        def callback(msg: ROSMessageType) -> bool:
            return bool(msg[field] < value)
        return callback

    def generate_callback_lesser_than(self, field: str, value: ROSMessageValue) -> ROSCallbackType:
        """
        Generate a base callback function that verifies
        if a given ROS message field is lesser than or equal to a certain reference value.

        :param field: The ROS message field.
        :type field: Any
        :param value: The reference value.
        :type value: Any
        :rtype: Callable[[Dict[str, Any]], bool]
        :return: A function that returns True if the ROS message field is lesser than or equal to the reference value.
        False otherwise.
        """
        def callback(msg: ROSMessageType) -> bool:
            return bool(msg[field] <= value)
        return callback

    def generate_callback_greater(self, field: str, value: ROSMessageValue) -> ROSCallbackType:
        """
        Generate a base callback function that verifies
        if a given ROS message field is greater than a certain reference value.

        :param field: The ROS message field.
        :type field: Any
        :param value: The reference value.
        :type value: Any
        :rtype: Callable[[Dict[str, Any]], bool]
        :return: A function that returns True if the ROS message field is greater than the reference value.
        False otherwise.
        """
        def callback(msg: ROSMessageType) -> bool:
            return bool(msg[field] > value)
        return callback

    def generate_callback_greater_than(self, field: str, value: ROSMessageValue) -> ROSCallbackType:
        """
        Generate a base callback function that verifies
        if a given ROS message field is greater than or equal to a certain reference value.

        :param field: The ROS message field.
        :type field: Any
        :param value: The reference value.
        :type value: Any
        :rtype: Callable[[Dict[str, Any]], bool]
        :return: A function that returns True if the ROS message field is greater than or equal to the reference value.
        False otherwise.
        """
        def callback(msg: ROSMessageType) -> bool:
            return bool(msg[field] >= value)
        return callback

    def generate_callback_iff(self, anterior: ROSCallbackType, posterior: ROSCallbackType) -> ROSCallbackType:
        """
        Generate a base callback function that
        retrives the value of a posterior function in case an anterior function returns True.

        :param anterior: The anterior function.
        :type anterior: Callable[[Dict[str, Any]], bool]
        :param posterior: The posterior function.
        :type posterior: Callable[[Dict[str, Any]], bool]
        :rtype: ROSCallbackType
        :return: A function that retrives the value of a posterior function in case an anterior function returns True.
        False otherwise.
        """
        def callback(msg: ROSMessageType) -> bool:
            if anterior(msg):
                return posterior(msg)
            return False
        return callback

    def generate_callback_and(self, anterior: ROSCallbackType, posterior: ROSCallbackType) -> ROSCallbackType:
        """
        Generate a base callback that
        verifies if both an anterior condition and a posterior condition return True.

        :param anterior: The anterior function.
        :type anterior: Callable[[Dict[str, Any]], bool]
        :param posterior: The posterior function.
        :type posterior: Callable[[Dict[str, Any]], bool]
        :rtype: ROSCallbackType
        :return: A function that returns True if both anterior and posterior functions also return True.
        False otherwise.
        """
        def callback(msg: ROSMessageType) -> bool:
            return anterior(msg) and posterior(msg)
        return callback

    # TODO: update to use base class HplExpression.
    def generate_callback(self, operator: HplBinaryOperator) -> ROSCallbackType:
        """
        Generates a callback function that verifies the same condition as a HplBinaryOperator.

        :param operator: The HplBinaryOperator holding information regarding the callback logic.
        :type operator: HplBinaryOperator
        :return: A ROS message handler callback function.
        :rtype: ROSCallbackType
        """
        arg1 = self.__extract_argument(operator.operand1)
        arg2 = self.__extract_argument(operator.operand2)

        if operator.op == '=':
            return self.generate_callback_equal(arg1, arg2)
        elif operator.op == '!=':
            return self.generate_callback_different(arg1, arg2)
        elif operator.op == '<':
            return self.generate_callback_lesser(arg1, arg2)
        elif operator.op == '<=':
            return self.generate_callback_lesser_than(arg1, arg2)
        elif operator.op == '>':
            return self.generate_callback_greater(arg1, arg2)
        elif operator.op == '>=':
            return self.generate_callback_greater_than(arg1, arg2)
        elif operator.op in ['iff', 'implies']:
            return self.generate_callback_iff(arg2, arg1)
        elif operator.op == 'and':
            return self.generate_callback_and(arg1, arg2)
        else:
            # TODO: create proper exception.
            raise Exception(f'Unsupported operator "{operator}".')

    def __extract_argument(
            self,
            operand: Union[HplBinaryOperator, HplFieldAccess, HplLiteral]
            ) -> Union[float, int, str, ROSCallbackType]:
        """
        Extract arguments from operators.

        :param operand: The operator to extract arguments from.
        :type operand: Union[HplBinaryOperator, HplFieldAccess, HplLiteral]
        :return: The argument value.
        :rtype: Union[float, int, str, ROSCallbackType]
        """
        if isinstance(operand, HplFieldAccess):
            return operand.field.value

        if isinstance(operand, HplLiteral):
            # NOTE: numerical primitive data values and 'bool'
            # have a different access mechanism than 'str'
            for t in [int, float, bool]:
                if isinstance(operand.value, t):
                    return operand.value
            return operand.value.value  # for 'str' typed values

        elif isinstance(operand, HplBinaryOperator):
            return self.generate_callback(operand)
