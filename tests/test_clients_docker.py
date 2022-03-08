import docker
import unittest
from rigelcore.clients import DockerClient
from rigelcore.exceptions import (
    DockerAPIError,
    DockerOperationError,
    InvalidDockerClientInstanceError,
    InvalidDockerImageNameError,

)
from unittest.mock import MagicMock, Mock, patch


class DockerClientTesting(unittest.TestCase):
    """
    Test suite for rigelcore.clients.DockerClient class.
    """

    def test_invalid_docker_client_instance_error(self) -> None:
        """
        Ensure that InvalidDockerClientInstanceError is thrown
        if an invalid instance of docker.client.DockerClient is provided.
        """
        with self.assertRaises(InvalidDockerClientInstanceError):
            DockerClient('invalid_docker_client_instance')

    @patch('rigelcore.clients.docker.docker.from_env')
    def test_docker_from_env_error(self, docker_mock: Mock) -> None:
        """
        Ensure that an instance of DockerAPIError is thrown
        if an error while trying to connect to the Docker daemon.
        """
        docker_mock.side_effect = docker.errors.DockerException

        with self.assertRaises(DockerAPIError):
            DockerClient()

    @patch('rigelcore.clients.docker.DockerClient.print_logs')
    @patch('rigelcore.clients.docker.docker.from_env')
    def test_client_image_build(self, docker_mock: Mock, print_mock: Mock) -> None:
        """
        Ensure that the creation of Docker images works as expected.
        """
        test_context_path = 'test_context_path'
        test_dockerfile_path = 'test_dockerfile_path'
        test_image = 'test_image'
        test_buildargs = {'TEST_VARIABLE': 'TEST_VALUE'}

        docker_api_mock_return_value = 'TestImageObject'
        docker_api_mock = MagicMock()
        docker_api_mock.api.build.return_value = docker_api_mock_return_value

        docker_mock.return_value = docker_api_mock

        docker_client = DockerClient()
        docker_client.build(test_context_path, test_dockerfile_path, test_image, test_buildargs)

        docker_api_mock.api.build.assert_called_once_with(
            path=test_context_path,
            decode=True,
            rm=True,
            dockerfile=test_dockerfile_path,
            tag=test_image,
            buildargs=test_buildargs
        )
        print_mock.assert_called_once_with(docker_api_mock_return_value)

    @patch('rigelcore.clients.docker.docker.from_env')
    def test_client_image_build_error(self, docker_mock: Mock) -> None:
        """
        Ensure that an instance of DockerAPIError is thrown
        if an error occurs while trying to build a Docker image.
        """

        test_exception = docker.errors.DockerException()

        docker_api_mock = MagicMock()
        docker_api_mock.api.build.side_effect = test_exception
        docker_mock.return_value = docker_api_mock

        with self.assertRaises(DockerAPIError) as context:
            docker_client = DockerClient()
            docker_client.build(
                'test_context_path',
                'test_dockerfile_path',
                'test_image',
                {'TEST_VARIABLE': 'TEST_VALUE'}
            )
        self.assertEqual(context.exception.kwargs['exception'], test_exception)

    def test_invalid_docker_image_name_error(self) -> None:
        """
        Ensure that InvalidDockerImageNameError is thrown if an invalid target image
        name is provided to function 'tag'.
        """
        test_target_image = 'invalid:image:name'
        with self.assertRaises(InvalidDockerImageNameError) as context:
            docker_client = DockerClient()
            docker_client.tag('test_source_image', test_target_image)
        self.assertEqual(context.exception.kwargs['image'], test_target_image)

    @patch('rigelcore.clients.docker.docker.from_env')
    def test_docker_image_name_split_default_tag(self, docker_mock: Mock) -> None:
        """
        Ensure that the target Docker image name is properly split when
        it does not contain character ':'.
        """
        test_source_image = 'test_source_image'
        test_target_image = 'test_target_image'

        docker_api_mock = MagicMock()

        docker_mock.return_value = docker_api_mock

        docker_client = DockerClient()
        docker_client.tag(test_source_image, test_target_image)

        docker_api_mock.api.tag.assert_called_once_with(
            image=test_source_image,
            repository=test_target_image,
            tag='latest'
        )

    @patch('rigelcore.clients.docker.docker.from_env')
    def test_docker_image_name_split_semicolon(self, docker_mock: Mock) -> None:
        """
        Ensure that the target Docker image name is properly split when
        it contains character ':'.
        """
        test_source_image = 'test_source_image'
        test_target_image = 'test_target_image'
        test_target_tag = 'test_target_tag'
        complete_test_target_image = f'{test_target_image}:{test_target_tag}'

        docker_api_mock = MagicMock()

        docker_mock.return_value = docker_api_mock

        docker_client = DockerClient()
        docker_client.tag(test_source_image, complete_test_target_image)

        docker_api_mock.api.tag.assert_called_once_with(
            image=test_source_image,
            repository=test_target_image,
            tag=test_target_tag
        )

    @patch('rigelcore.clients.docker.docker.from_env')
    def test_docker_image_tag_api_error(self, docker_mock: Mock) -> None:
        """
        Ensure that an instance of DockerAPIError is thrown
        if an error occurs while attempting to tag a Docker image.
        """

        test_exception = docker.errors.DockerException()

        docker_api_mock = MagicMock()
        docker_api_mock.api.tag.side_effect = test_exception
        docker_mock.return_value = docker_api_mock

        with self.assertRaises(DockerAPIError) as context:
            docker_client = DockerClient()
            docker_client.tag(
                'test_source_image',
                'test_target_image'
            )
        self.assertEqual(context.exception.kwargs['exception'], test_exception)

    @patch('rigelcore.clients.docker.docker.from_env')
    def test_invalid_image_registry_error(self, docker_mock: Mock) -> None:
        """
        Ensure that DockerAPIError is thrown
        if an error occurs while attempting to login to a Docker registry.
        """

        test_exception = docker.errors.DockerException()

        docker_api_mock = MagicMock()
        docker_api_mock.api.login.side_effect = test_exception
        docker_mock.return_value = docker_api_mock

        with self.assertRaises(DockerAPIError) as context:
            docker_client = DockerClient()
            docker_client.login('test_registry', 'test_username', 'test_password')
        self.assertEqual(context.exception.kwargs['exception'], test_exception)

    @patch('rigelcore.clients.docker.docker.from_env')
    def test_client_login(self, docker_mock: Mock) -> None:
        """
        Ensure that login information is properly passed.
        """
        test_registry = 'test_registry'
        test_username = 'test_username'
        test_password = 'test_password'

        docker_api_mock = MagicMock()

        docker_mock.return_value = docker_api_mock

        docker_client = DockerClient()
        docker_client.login(test_registry, test_username, test_password)

        docker_api_mock.api.login.assert_called_once_with(
            username=test_username,
            password=test_password,
            registry=test_registry
        )

    @patch('rigelcore.clients.docker.DockerClient.print_logs')
    @patch('rigelcore.clients.docker.docker.from_env')
    def test_client_image_push(self, docker_mock: Mock, print_mock: Mock) -> None:
        """
        Ensure that the deploy of Docker images works as expected.
        """
        test_image = 'test_image'

        docker_api_mock_return_value = 'TestImageObject'
        docker_api_mock = MagicMock()
        docker_api_mock.api.push.return_value = docker_api_mock_return_value

        docker_mock.return_value = docker_api_mock

        docker_client = DockerClient()
        docker_client.push(test_image)

        docker_api_mock.api.push.assert_called_once_with(
            test_image,
            stream=True,
            decode=True,
        )
        print_mock.assert_called_once_with(docker_api_mock_return_value)

    @patch('rigelcore.clients.docker.DockerClient.print_logs')
    @patch('rigelcore.clients.docker.docker.from_env')
    def test_client_image_push_api_error(self, docker_mock: Mock, print_mock: Mock) -> None:
        """
        Ensure that an instance of DockerAPIError is thrown
        if an error occurs while attempting to push a Docker image to a registry.
        """

        test_exception = docker.errors.DockerException()

        docker_api_mock = MagicMock()
        docker_api_mock.api.push.side_effect = test_exception
        docker_mock.return_value = docker_api_mock

        with self.assertRaises(DockerAPIError) as context:
            docker_client = DockerClient()
            docker_client.push('test_image')
        self.assertEqual(context.exception.kwargs['exception'], test_exception)

    @patch('rigelcore.clients.docker.DockerLogPrinter.log')
    @patch('rigelcore.clients.docker.docker.from_env')
    def test_docker_operation_error(self, docker_mock: Mock, logger_mock: Mock) -> None:
        """
        Ensure that DockerOperationError is thrown whenever an error log is found.
        """
        test_error_message = 'Test error log message.'
        log = {'error': test_error_message}

        image_mock = MagicMock()
        image_mock.__iter__.return_value = [log]

        with self.assertRaises(DockerOperationError) as context:
            docker_client = DockerClient()
            docker_client.print_logs(image_mock)
        self.assertEqual(context.exception.kwargs['msg'], test_error_message)

        logger_mock.assert_called_once_with(log)

    @patch('rigelcore.clients.docker.docker.from_env')
    def test_docker_network_exists_true(self, docker_mock: Mock) -> None:
        """
        Ensure that the mechanism to verify if a Docker network already exists
        is working as expected.
        """
        test_docker_network = 'test_docker_network'

        docker_networks_mock = MagicMock()
        docker_networks_mock.networks.list.return_value = True
        docker_mock.return_value = docker_networks_mock

        docker_client = DockerClient()
        network_exists = docker_client.network_exists(test_docker_network)

        docker_networks_mock.networks.list.assert_called_once_with(names=[test_docker_network])
        self.assertTrue(network_exists)

    @patch('rigelcore.clients.docker.docker.from_env')
    def test_docker_network_exists_false(self, docker_mock: Mock) -> None:
        """
        Ensure that the mechanism to verify if a Docker network already exists
        is working as expected.
        """
        test_docker_network = 'test_docker_network'

        docker_networks_mock = MagicMock()
        docker_networks_mock.networks.list.return_value = False
        docker_mock.return_value = docker_networks_mock

        docker_client = DockerClient()
        network_exists = docker_client.network_exists(test_docker_network)

        docker_networks_mock.networks.list.assert_called_once_with(names=[test_docker_network])
        self.assertFalse(network_exists)

    @patch('rigelcore.clients.docker.docker.from_env')
    @patch('rigelcore.clients.docker.DockerClient.network_exists')
    def test_create_docker_network_new(self, network_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that the mechanism to create new Docker networks works as expected.
        """

        test_docker_network_name = 'test_docker_network_name'
        test_docker_network_driver = 'test_docker_network_driver'

        docker_networks_mock = MagicMock()
        docker_mock.return_value = docker_networks_mock
        network_mock.return_value = False

        docker_client = DockerClient()
        docker_client.create_network(
            test_docker_network_name,
            test_docker_network_driver
        )

        network_mock.assert_called_once_with(test_docker_network_name)
        docker_networks_mock.networks.create.assert_called_once_with(
            test_docker_network_name,
            driver=test_docker_network_driver
        )

    @patch('rigelcore.clients.docker.docker.from_env')
    @patch('rigelcore.clients.docker.DockerClient.network_exists')
    def test_create_docker_network_existent(self, network_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that the mechanism to create new Docker networks first
        verifies if a given Docker network exists before creating it.
        """

        test_docker_network_name = 'test_docker_network_name'
        test_docker_network_driver = 'test_docker_network_driver'

        docker_networks_mock = MagicMock()
        docker_mock.return_value = docker_networks_mock
        network_mock.return_value = True

        docker_client = DockerClient()
        docker_client.create_network(
            test_docker_network_name,
            test_docker_network_driver
        )

        network_mock.assert_called_once_with(test_docker_network_name)
        docker_networks_mock.networks.create.assert_not_called()

    @patch('rigelcore.clients.docker.docker.from_env')
    @patch('rigelcore.clients.docker.DockerClient.network_exists')
    def test_docker_create_network_api_error_(self, network_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that an instance of DockerAPI error is thrown
        if an error occurs while creating a new Docker network using the Docker API.
        """

        test_exception = docker.errors.DockerException()

        docker_network_mock = MagicMock()
        docker_network_mock.networks.create.side_effect = test_exception
        docker_mock.return_value = docker_network_mock

        network_mock.return_value = False

        with self.assertRaises(DockerAPIError) as context:
            docker_client = DockerClient()
            docker_client.create_network(
                'test_docker_network_name',
                'test_docker_network_driver'
            )
        self.assertEqual(context.exception.kwargs['exception'], test_exception)


if __name__ == '__main__':
    unittest.main()
