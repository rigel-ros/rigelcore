import unittest
from rigelcore.exceptions import (
    DockerImageNotFoundError,
    DockerOperationError,
    InvalidDockerImageNameError,
    InvalidImageRegistryError,
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


if __name__ == '__main__':
    unittest.main()
