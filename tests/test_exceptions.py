import unittest
from rigelcore.exceptions import (
    DockerImageNotFoundError,
    DockerNotFoundError,
    DockerOperationError,
    InvalidDockerClientInstanceError,
    InvalidDockerDriverError,
    InvalidDockerImageNameError,
    InvalidImageRegistryError,
    InvalidValueError,
    MissingRequiredFieldError,
    UndeclaredEnvironmentVariableError,
    UndeclaredGlobalVariableError,
    UndeclaredValueError,
    RigelError
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

    def test_docker_invalid_image_name_error(self) -> None:
        """
        Ensure that instances of InvalidDockerImageNameError are thrown as expected.
        """
        test_image = 'test_image'
        err = InvalidDockerImageNameError(image=test_image)
        self.assertEqual(err.code, 2)
        self.assertEqual(err.kwargs['image'], test_image)

    def test_docker_image_not_found_error(self) -> None:
        """
        Ensure that instances of DockerImageNotFoundError are thrown as expected.
        """
        test_image = 'test_image'
        err = DockerImageNotFoundError(image=test_image)
        self.assertEqual(err.code, 3)
        self.assertEqual(err.kwargs['image'], test_image)

    def test_docker_invalid_image_registry_error(self) -> None:
        """
        Ensure that instances of InvalidImageRegistryError are thrown as expected.
        """
        test_registry = 'test_registry'
        err = InvalidImageRegistryError(registry=test_registry)
        self.assertEqual(err.code, 4)
        self.assertEqual(err.kwargs['registry'], 'test_registry')

    def test_docker_operation_error(self) -> None:
        """
        Ensure that instances of DockerOperationError are thrown as expected.
        """
        test_msg = 'test_msg'
        err = DockerOperationError(msg=test_msg)
        self.assertEqual(err.code, 5)
        self.assertEqual(err.kwargs['msg'], test_msg)

    def test_undeclared_value_error(self) -> None:
        """
        Ensure that instances of UndeclaredValueError are thrown as expected.
        """
        test_field = 'test_field'
        err = UndeclaredValueError(field=test_field)
        self.assertEqual(err.code, 6)
        self.assertEqual(err.kwargs['field'], test_field)

    def test_invalid_value_error(self) -> None:
        """
        Ensure that instances of InvalidValueError are thrown as expected.
        """
        test_instance_type = str
        test_field = 'test_field'
        err = InvalidValueError(instance_type=test_instance_type, field=test_field)
        self.assertEqual(err.code, 7)
        self.assertEqual(err.kwargs['instance_type'], test_instance_type)
        self.assertEqual(err.kwargs['field'], test_field)

    def test_missing_required_field_error(self) -> None:
        """
        Ensure that instances of MissingRequiredFieldError are thrown as expected.
        """
        test_field = 'test_field'
        err = MissingRequiredFieldError(field=test_field)
        self.assertEqual(err.code, 8)
        self.assertEqual(err.kwargs['field'], test_field)

    def test_undeclared_environment_variable_error(self) -> None:
        """
        Ensure that instances of UndeclaredEnvironmentVariableError are thrown as expected.
        """
        test_env = 'TEST_ENV'
        err = UndeclaredEnvironmentVariableError(env=test_env)
        self.assertEqual(err.code, 9)
        self.assertEqual(err.kwargs['env'], test_env)

    def test_undeclared_global_variable_error(self) -> None:
        """
        Ensure that instances of UndeclaredGlobalVariableError are thrown as expected.
        """
        test_field = 'test_field'
        test_var = 'test_var'
        err = UndeclaredGlobalVariableError(field=test_field, var=test_var)
        self.assertEqual(err.code, 10)
        self.assertEqual(err.kwargs['field'], test_field)
        self.assertEqual(err.kwargs['var'], test_var)

    def test_docker_not_found_error(self) -> None:
        """
        Ensure that instances of DockerNotFoundError are thrown as expected.
        """
        err = DockerNotFoundError()
        self.assertEqual(err.code, 11)

    def test_invalid_docker_client_instance_error(self) -> None:
        """
        Ensure that instances of InvalidDockerClientInstanceError are thrown as expected.
        """
        err = InvalidDockerClientInstanceError()
        self.assertEqual(err.code, 12)

    def test_invalid_docker_driver_error(self) -> None:
        """
        Ensure that instances of InvalidDockerDriverError are thrown as expected.
        """
        test_docker_driver = 'test_docker_driver'
        err = InvalidDockerDriverError(driver=test_docker_driver)
        self.assertEqual(err.code, 13)
        self.assertEqual(err.kwargs['driver'], test_docker_driver)


if __name__ == '__main__':
    unittest.main()
