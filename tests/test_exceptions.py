import docker
import pydantic
import unittest
from rigelcore.exceptions import (
    DockerAPIError,
    DockerOperationError,
    InvalidDockerClientInstanceError,
    InvalidDockerImageNameError,
    PydanticValidationError,
    RigelError,
    UndeclaredEnvironmentVariableError,
    UndeclaredGlobalVariableError
)


class ExceptionTesting(unittest.TestCase):
    """
    Test suite for rigelcore.exceptions.RigelError class and all its subclasses.
    """

    def test_base_rigel_error(self) -> None:
        """
        Ensure that instances of RigelError are thrown as expected.
        """
        err = RigelError()
        self.assertEqual(err.code, 1)

    def test_docker_api_error(self) -> None:
        """
        Ensure that instances of DockerAPIError are thrown as expected.
        """
        exception = docker.errors.DockerException()
        err = DockerAPIError(exception=exception)
        self.assertEqual(err.code, 2)
        self.assertEqual(err.kwargs['exception'], exception)
        self.assertTrue(isinstance(err, RigelError))

    def test_docker_invalid_image_name_error(self) -> None:
        """
        Ensure that instances of InvalidDockerImageNameError are thrown as expected.
        """
        test_image = 'test_image'
        err = InvalidDockerImageNameError(image=test_image)
        self.assertEqual(err.code, 3)
        self.assertEqual(err.kwargs['image'], test_image)
        self.assertTrue(isinstance(err, RigelError))

    def test_invalid_docker_client_instance_error(self) -> None:
        """
        Ensure that instances of InvalidDockerClientInstanceError are thrown as expected.
        """
        err = InvalidDockerClientInstanceError()
        self.assertEqual(err.code, 4)
        self.assertTrue(isinstance(err, RigelError))

    def test_docker_operation_error(self) -> None:
        """
        Ensure that instances of DockerOperationError are thrown as expected.
        """
        test_msg = 'test_msg'
        err = DockerOperationError(msg=test_msg)
        self.assertEqual(err.code, 5)
        self.assertEqual(err.kwargs['msg'], test_msg)
        self.assertTrue(isinstance(err, RigelError))

    def test_pydantic_validation_error(self) -> None:
        """
        Ensure that instances of PydanticValidationError are thrown as expected.
        """

        @pydantic.validate_arguments
        def test_sum(a: int, b: int) -> int:
            return a + b

        try:
            test_sum('a', 12)  # type: ignore [arg-type]
        except pydantic.ValidationError as exception:

            err = PydanticValidationError(exception=exception)
            self.assertEqual(err.code, 6)
            self.assertEqual(err.kwargs['exception'], exception)
            self.assertTrue(isinstance(err, RigelError))

    def test_undeclared_environment_variable_error(self) -> None:
        """
        Ensure that instances of UndeclaredEnvironmentVariableError are thrown as expected.
        """
        test_env = 'TEST_ENV'
        err = UndeclaredEnvironmentVariableError(env=test_env)
        self.assertEqual(err.code, 7)
        self.assertEqual(err.kwargs['env'], test_env)
        self.assertTrue(isinstance(err, RigelError))

    def test_undeclared_global_variable_error(self) -> None:
        """
        Ensure that instances of UndeclaredGlobalVariableError are thrown as expected.
        """
        test_field = 'test_field'
        test_var = 'test_var'
        err = UndeclaredGlobalVariableError(field=test_field, var=test_var)
        self.assertEqual(err.code, 8)
        self.assertEqual(err.kwargs['field'], test_field)
        self.assertEqual(err.kwargs['var'], test_var)
        self.assertTrue(isinstance(err, RigelError))


if __name__ == '__main__':
    unittest.main()
