import python_on_whales
import unittest
from rigelcore.clients import DockerClient
from rigelcore.exceptions import (
    DockerAPIError,
    InvalidDockerClientInstanceError
)
from typing import cast
from unittest.mock import MagicMock, Mock, patch


class DockerClientTesting(unittest.TestCase):
    """
    Test suite for rigelcore.clients.DockerClient class.
    """

    def test_invalid_docker_client_instance_error(self) -> None:
        """
        Ensure that InvalidDockerClientInstanceError is thrown
        if an invalid instance of python_on_whales.docker_client.DockerClient is provided.
        """
        client_mock = cast(python_on_whales.docker_client.DockerClient, Mock())
        with self.assertRaises(InvalidDockerClientInstanceError):
            DockerClient(client_mock)

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    def test_docker_get_image_error(self, docker_mock: Mock) -> None:
        """
        Ensure that an instance of DockerAPIError is thrown
        if an error occurs while searching for a Docker image using the Docker API.
        """
        test_exception = python_on_whales.exceptions.DockerException(['test_command'], 0)

        docker_mock.image.exists.side_effect = test_exception

        with self.assertRaises(DockerAPIError) as context:
            docker_client = DockerClient()
            docker_client.get_image('test_docker_image_name')
        self.assertEqual(context.exception.kwargs['exception'], test_exception)

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    def test_docker_get_image_none(self, docker_mock: Mock) -> None:
        """
        Ensure that the mechanism to retrieve existing Docker images
        works as expected when the specified Docker image does not exist.
        """
        docker_mock.image.exists.return_value = False
        test_image_name = 'test_docker_image_name'

        docker_client = DockerClient()
        image = docker_client.get_image(test_image_name)
        docker_mock.image.exists.assert_called_once_with(test_image_name)
        self.assertIsNone(image)

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    def test_docker_get_image(self, docker_mock: Mock) -> None:
        """
        Ensure that the mechanism to retrieve existing Docker images works as expected.
        """
        docker_mock.image.inspect.return_value = True
        test_image_name = 'test_docker_image_name'

        docker_client = DockerClient()
        result = docker_client.get_image(test_image_name)
        docker_mock.image.inspect.called_once_with(test_image_name)
        self.assertTrue(result)

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    def test_client_image_build(self, docker_mock: Mock) -> None:
        """
        Ensure that the creation of Docker images works as expected.
        """
        test_context_path = 'test_context_path'
        test_image = 'test_image'
        test_buildargs = {'TEST_VARIABLE': 'TEST_VALUE'}
        test_platforms = ['test_platform']

        docker_client = DockerClient()
        docker_client.build_image(
            test_context_path,
            tags=test_image,
            build_args=test_buildargs,
            platforms=test_platforms
        )

        docker_mock.build.assert_called_once_with(
            test_context_path,
            tags=test_image,
            build_args=test_buildargs,
            platforms=test_platforms
        )

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    def test_client_image_build_error(self, docker_mock: Mock) -> None:
        """
        Ensure that an instance of DockerAPIError is thrown
        if an error occurs while trying to build a Docker image.
        """
        test_exception = python_on_whales.exceptions.DockerException(['test_command'], 0)
        docker_mock.build.side_effect = test_exception

        with self.assertRaises(DockerAPIError) as context:
            docker_client = DockerClient()
            docker_client.build_image('test_context_path')

        self.assertEqual(context.exception.kwargs['exception'], test_exception)

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    def test_invalid_docker_image_name_error(self, docker_mock: Mock) -> None:
        """
        Ensure that DockerAPIError is thrown if an invalid target image
        name is provided to function 'tag'.
        """
        test_exception = python_on_whales.exceptions.DockerException(['test_command'], 0)
        docker_mock.image.tag.side_effect = test_exception

        with self.assertRaises(DockerAPIError) as context:
            docker_client = DockerClient()
            docker_client.tag_image('test_source_image', 'invalid:image:name')

        self.assertEqual(context.exception.kwargs['exception'], test_exception)

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    def test_docker_image_name_split_default_tag(self, docker_mock: Mock) -> None:
        """
        Ensure that the target Docker image name is properly split when
        it does not contain character ':'.
        """
        test_source_image = 'test_source_image'
        test_target_image = 'test_target_image'

        docker_client = DockerClient()
        docker_client.tag_image(test_source_image, test_target_image)

        docker_mock.image.tag.assert_called_once_with(
            test_source_image,
            test_target_image
        )

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    def test_invalid_image_registry_error(self, docker_mock: Mock) -> None:
        """
        Ensure that DockerAPIError is thrown
        if an error occurs while attempting to login to a Docker registry.
        """
        test_exception = python_on_whales.exceptions.DockerException(['test_command'], 0)
        docker_mock.login.side_effect = test_exception

        with self.assertRaises(DockerAPIError) as context:
            docker_client = DockerClient()
            docker_client.login('test_registry', 'test_username', 'test_password')
        self.assertEqual(context.exception.kwargs['exception'], test_exception)

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    def test_client_login(self, docker_mock: Mock) -> None:
        """
        Ensure that login information is properly passed.
        """
        test_registry = 'test_registry'
        test_username = 'test_username'
        test_password = 'test_password'

        docker_client = DockerClient()
        docker_client.login(test_registry, test_username, test_password)

        docker_mock.login.assert_called_once_with(
            username=test_username,
            password=test_password,
            server=test_registry
        )

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    def test_logout_error(self, docker_mock: Mock) -> None:
        """
        Ensure that DockerAPIError is thrown
        if an error occurs while attempting to logout from a Docker registry.
        """
        test_exception = python_on_whales.exceptions.DockerException(['test_command'], 0)
        docker_mock.logout.side_effect = test_exception

        with self.assertRaises(DockerAPIError) as context:
            docker_client = DockerClient()
            docker_client.logout('test_registry')
        self.assertEqual(context.exception.kwargs['exception'], test_exception)

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    def test_client_logout(self, docker_mock: Mock) -> None:
        """
        Ensure that logout information is properly passed.
        """
        test_registry = 'test_registry'

        docker_client = DockerClient()
        docker_client.logout(test_registry)

        docker_mock.logout.assert_called_once_with(test_registry)

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    def test_client_image_push(self, docker_mock: Mock) -> None:
        """
        Ensure that the deploy of Docker images works as expected.
        """
        test_image = 'test_image'

        docker_client = DockerClient()
        docker_client.push_image(test_image)

        docker_mock.image.push.assert_called_once_with(test_image)

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    def test_client_image_push_api_error(self, docker_mock: Mock) -> None:
        """
        Ensure that an instance of DockerAPIError is thrown
        if an error occurs while attempting to push a Docker image to a registry.
        """
        test_exception = python_on_whales.exceptions.DockerException(['test_command'], 0)
        docker_mock.image.push.side_effect = test_exception

        with self.assertRaises(DockerAPIError) as context:
            docker_client = DockerClient()
            docker_client.push_image('test_image')
        self.assertEqual(context.exception.kwargs['exception'], test_exception)

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    def test_docker_builder_exists_true(self, docker_mock: Mock) -> None:
        """
        Ensure that the mechanism to verify if a Docker builder already exists
        is working as expected.
        """
        test_docker_builder = 'test_docker_builder'

        test_builder = Mock()
        docker_mock.buildx.inspect.return_value = test_builder

        docker_client = DockerClient()
        builder = docker_client.get_builder(test_docker_builder)

        docker_mock.buildx.inspect.assert_called_once_with(test_docker_builder)
        self.assertEqual(builder, test_builder)

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    def test_docker_builder_exists_false(self, docker_mock: Mock) -> None:
        """
        Ensure that the mechanism to verify if a Docker builder already exists
        is working as expected.
        """
        test_docker_builder = 'test_docker_builder'

        test_exception = python_on_whales.exceptions.DockerException(['test_command'], 0)
        docker_mock.buildx.inspect.side_effect = test_exception

        docker_client = DockerClient()
        builder = docker_client.get_builder(test_docker_builder)

        docker_mock.buildx.inspect.assert_called_once_with(test_docker_builder)
        self.assertIsNone(builder)

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    @patch('rigelcore.clients.docker.DockerClient.get_builder')
    def test_create_docker_builder_new_defaults(self, builder_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that the mechanism to create new Docker networks works as expected
        when no 'use' value is provided.
        """
        test_docker_builder_name = 'test_docker_builder_name'

        builder_mock.return_value = None

        docker_client = DockerClient()
        docker_client.create_builder(test_docker_builder_name)

        builder_mock.assert_called_once_with(test_docker_builder_name)
        docker_mock.buildx.create.assert_called_once_with(
            name=test_docker_builder_name,
            use=True,
            driver='docker-container'
        )

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    @patch('rigelcore.clients.docker.DockerClient.get_builder')
    def test_create_docker_builder_new(self, builder_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that the mechanism to create new Docker networks works as expected.
        """

        test_docker_builder_name = 'test_docker_builder_name'
        test_docker_builder_use = cast(bool, str('test_docker_builder_use'))
        test_docker_driver = 'test_docker_driver'

        builder_mock.return_value = None

        docker_client = DockerClient()
        docker_client.create_builder(
            test_docker_builder_name,
            use=test_docker_builder_use,
            driver=test_docker_driver
        )

        builder_mock.assert_called_once_with(test_docker_builder_name)
        docker_mock.buildx.create.assert_called_once_with(
            name=test_docker_builder_name,
            use=test_docker_builder_use,
            driver=test_docker_driver
        )

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    @patch('rigelcore.clients.docker.DockerClient.get_builder')
    def test_create_docker_builder_existent(self, builder_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that the mechanism to create new Docker builders first
        verifies if a given Docker builder exists before creating it.
        """
        test_docker_builder_name = 'test_docker_builder_name'
        test_docker_builder_use = cast(bool, str('test_docker_builder_use'))

        test_builder = Mock()
        builder_mock.return_value = test_builder

        docker_client = DockerClient()
        builder = docker_client.create_builder(
            test_docker_builder_name,
            use=test_docker_builder_use
        )

        builder_mock.assert_called_once_with(test_docker_builder_name)
        docker_mock.buildx.create.assert_not_called()
        self.assertEqual(builder, test_builder)

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    @patch('rigelcore.clients.docker.DockerClient.get_builder')
    def test_docker_create_builder_api_error(self, builder_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that an instance of DockerAPIError is thrown
        if an error occurs while creating a new Docker builder using the Docker API.
        """
        test_exception = python_on_whales.exceptions.DockerException(['test_command'], 0)
        docker_mock.buildx.create.side_effect = test_exception

        builder_mock.return_value = None

        with self.assertRaises(DockerAPIError) as context:
            docker_client = DockerClient()
            docker_client.create_builder(
                'test_docker_builder_name',
                use=False
            )
        self.assertEqual(context.exception.kwargs['exception'], test_exception)

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    @patch('rigelcore.clients.docker.DockerClient.get_builder')
    def test_docker_remove_builder_api_error(self, builder_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that an instance of DockerAPIError is thrown
        if an error occurs while deleting a Docker builder using the Docker API.
        """
        test_builder_name = 'test_builder_name'

        test_exception = python_on_whales.exceptions.DockerException(['test_command'], 0)
        docker_mock.buildx.remove.side_effect = test_exception

        test_builder = Mock()
        builder_mock.return_value = test_builder

        with self.assertRaises(DockerAPIError) as context:
            docker_client = DockerClient()
            docker_client.remove_builder(test_builder_name)

        builder_mock.assert_called_once_with(test_builder_name)
        self.assertEqual(context.exception.kwargs['exception'], test_exception)

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    @patch('rigelcore.clients.docker.DockerClient.get_builder')
    def test_docker_remove_builder_unexistent(self, builder_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that a builder delete Docker API call is only made if a given builder exists.
        """
        test_builder_name = 'test_builder_name'

        builder_mock.return_value = False

        docker_client = DockerClient()
        docker_client.remove_builder(test_builder_name)

        builder_mock.assert_called_once_with(test_builder_name)
        docker_mock.buildx.remove.assert_not_called()

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    @patch('rigelcore.clients.docker.DockerClient.get_builder')
    def test_docker_remove_builder_existent(self, builder_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that a network delete Docker API call is only made if a given network exists.
        """
        test_builder_name = 'test_network_name'

        test_builder = Mock()
        builder_mock.return_value = test_builder

        docker_client = DockerClient()
        docker_client.remove_builder(test_builder_name)

        builder_mock.assert_called_once_with(test_builder_name)
        docker_mock.buildx.remove.assert_called_once_with(test_builder)

    #################

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    def test_docker_network_exists_true(self, docker_mock: Mock) -> None:
        """
        Ensure that the mechanism to verify if a Docker network already exists
        is working as expected.
        """
        test_docker_network = 'test_docker_network'

        test_network = Mock()
        docker_mock.network.inspect.return_value = test_network

        docker_client = DockerClient()
        network = docker_client.get_network(test_docker_network)

        docker_mock.network.inspect.assert_called_once_with(test_docker_network)
        self.assertEqual(network, test_network)

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    def test_docker_network_exists_false(self, docker_mock: Mock) -> None:
        """
        Ensure that the mechanism to verify if a Docker network already exists
        is working as expected.
        """
        test_docker_network = 'test_docker_network'

        test_exception = python_on_whales.exceptions.DockerException(['test_command'], 0)
        docker_mock.network.inspect.side_effect = test_exception

        docker_client = DockerClient()
        network = docker_client.get_network(test_docker_network)

        docker_mock.network.inspect.assert_called_once_with(test_docker_network)
        self.assertIsNone(network)

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    @patch('rigelcore.clients.docker.DockerClient.get_network')
    def test_create_docker_network_new(self, network_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that the mechanism to create new Docker networks works as expected.
        """

        test_docker_network_name = 'test_docker_network_name'
        test_docker_network_driver = 'test_docker_network_driver'

        network_mock.return_value = None

        docker_client = DockerClient()
        docker_client.create_network(
            test_docker_network_name,
            test_docker_network_driver
        )

        network_mock.assert_called_once_with(test_docker_network_name)
        docker_mock.network.create.assert_called_once_with(
            test_docker_network_name,
            driver=test_docker_network_driver
        )

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    @patch('rigelcore.clients.docker.DockerClient.get_network')
    def test_create_docker_network_existent(self, network_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that the mechanism to create new Docker networks first
        verifies if a given Docker network exists before creating it.
        """
        test_docker_network_name = 'test_docker_network_name'
        test_docker_network_driver = 'test_docker_network_driver'

        test_network = Mock()
        network_mock.return_value = test_network

        docker_client = DockerClient()
        network = docker_client.create_network(
            test_docker_network_name,
            test_docker_network_driver
        )

        network_mock.assert_called_once_with(test_docker_network_name)
        docker_mock.network.create.assert_not_called()
        self.assertEqual(network, test_network)

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    @patch('rigelcore.clients.docker.DockerClient.get_network')
    def test_docker_create_network_api_error(self, network_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that an instance of DockerAPIError is thrown
        if an error occurs while creating a new Docker network using the Docker API.
        """
        test_exception = python_on_whales.exceptions.DockerException(['test_command'], 0)
        docker_mock.network.create.side_effect = test_exception

        network_mock.return_value = None

        with self.assertRaises(DockerAPIError) as context:
            docker_client = DockerClient()
            docker_client.create_network(
                'test_docker_network_name',
                'test_docker_network_driver'
            )
        self.assertEqual(context.exception.kwargs['exception'], test_exception)

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    @patch('rigelcore.clients.docker.DockerClient.get_network')
    def test_docker_remove_network_api_error(self, network_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that an instance of DockerAPIError is thrown
        if an error occurs while deleting a Docker network using the Docker API.
        """
        test_network_name = 'test_network_name'

        test_exception = python_on_whales.exceptions.DockerException(['test_command'], 0)
        docker_mock.network.remove.side_effect = test_exception

        test_network = Mock()
        network_mock.return_value = test_network

        with self.assertRaises(DockerAPIError) as context:
            docker_client = DockerClient()
            docker_client.remove_network(test_network_name)

        network_mock.assert_called_once_with(test_network_name)
        self.assertEqual(context.exception.kwargs['exception'], test_exception)

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    @patch('rigelcore.clients.docker.DockerClient.get_network')
    def test_docker_remove_network_unexistent(self, network_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that a network delete Docker API call is only made if a given network exists.
        """
        test_network_name = 'test_network_name'

        network_mock.return_value = False

        docker_client = DockerClient()
        docker_client.remove_network(test_network_name)

        network_mock.assert_called_once_with(test_network_name)
        docker_mock.network.remove.assert_not_called()

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    @patch('rigelcore.clients.docker.DockerClient.get_network')
    def test_docker_remove_network_existent(self, network_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that a network delete Docker API call is only made if a given network exists.
        """
        test_network_name = 'test_network_name'

        test_network = Mock()
        network_mock.return_value = test_network

        docker_client = DockerClient()
        docker_client.remove_network(test_network_name)

        network_mock.assert_called_once_with(test_network_name)
        docker_mock.network.remove.assert_called_once_with(test_network)

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    def test_docker_get_container_api_error(self, docker_mock: Mock) -> None:
        """
        Ensure that an instance of DockerAPIError is thrown
        if an error occurs while retrieving a Docker container information using the Docker API.
        """
        test_exception = python_on_whales.exceptions.DockerException(['test_command'], 0)
        docker_mock.container.exists.side_effect = test_exception

        with self.assertRaises(DockerAPIError) as context:
            docker_client = DockerClient()
            docker_client.get_container('test_docker_container')

        self.assertEqual(context.exception.kwargs['exception'], test_exception)

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    def test_docker_get_container_exists(self, docker_mock: Mock) -> None:
        """
        Ensure that the mechanism to retrieve Docker containers works as expected.
        """
        test_docker_container_name = 'test_docker_container_name'
        test_container = Mock()

        docker_mock.container.exists.return_value = True
        docker_mock.container.inspect.return_value = test_container

        docker_client = DockerClient()
        container = docker_client.get_container(test_docker_container_name)

        docker_mock.container.exists.assert_called_once_with(test_docker_container_name)
        docker_mock.container.inspect.assert_called_once_with(test_docker_container_name)
        self.assertEqual(container, test_container)

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    def test_docker_get_container_unexistent(self, docker_mock: Mock) -> None:
        """
        Ensure that the mechanism to retrieve Docker containers works as expected
        if the specified Docker container does not exist.
        """
        test_docker_container_name = 'test_docker_container_name'

        docker_mock.container.exists.return_value = False

        docker_client = DockerClient()
        container = docker_client.get_container(test_docker_container_name)

        docker_mock.container.exists.assert_called_once_with(test_docker_container_name)
        self.assertIsNone(container)

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    @patch('rigelcore.clients.docker.DockerClient.get_container')
    def test_docker_remove_container_api_error(self, container_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that a DockerAPIError instance is thrown
        if an error occurs while removing a Docker container using Docker API calls.
        """
        test_exception = python_on_whales.exceptions.DockerException(['test_command'], 0)

        container_instance_mock = MagicMock()
        container_instance_mock.__bool__.return_value = True
        container_instance_mock.remove.side_effect = test_exception
        container_mock.return_value = container_instance_mock

        with self.assertRaises(DockerAPIError) as context:
            docker_client = DockerClient()
            docker_client.remove_container('test_docker_container_name')
        self.assertEqual(context.exception.kwargs['exception'], test_exception)

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    @patch('rigelcore.clients.docker.DockerClient.get_container')
    def test_docker_remove_container_exists(self, container_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that the mecanism to delete Docker containers works as expected.
        """
        test_docker_container_name = 'test_docker_container_name'

        container_instance_mock = MagicMock()
        container_instance_mock.__bool__.return_value = True
        container_mock.return_value = container_instance_mock

        docker_client = DockerClient()
        docker_client.remove_container(test_docker_container_name)

        container_mock.assert_called_once_with(test_docker_container_name)
        container_instance_mock.remove.assert_called_once_with(force=True, volumes=True)

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    @patch('rigelcore.clients.docker.DockerClient.get_container')
    def test_docker_remove_container_unexistent(self, container_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that the mecanism to delete Docker containers works as expected
        when the specified Docker container does not exist.
        """
        test_docker_container_name = 'test_docker_container_name'

        container_instance_mock = MagicMock()
        container_instance_mock.__bool__.return_value = False
        container_mock.return_value = container_instance_mock

        docker_client = DockerClient()
        docker_client.remove_container(test_docker_container_name)

        container_mock.assert_called_once_with(test_docker_container_name)
        container_instance_mock.remove.assert_not_called()

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    @patch('rigelcore.clients.docker.DockerClient.get_container')
    def test_docker_run_container_api_error(self, container_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that a DockerAPIError instance is thrown
        if an error occurs while running a Docker container using Docker API calls.
        """
        test_exception = python_on_whales.exceptions.DockerException(['test_command'], 0)
        docker_mock.container.run.side_effect = test_exception

        container_instance_mock = MagicMock()
        container_instance_mock.__bool__.return_value = False
        container_mock.return_value = container_instance_mock

        with self.assertRaises(DockerAPIError) as context:
            docker_client = DockerClient()
            docker_client.run_container(
                'test_docker_container_name',
                'test_docker_image_name'
            )

        self.assertEqual(context.exception.kwargs['exception'], test_exception)

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    @patch('rigelcore.clients.docker.DockerClient.get_container')
    def test_docker_run_container_exists(self, container_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that a Docker container is only run if no other Docker container
        exists with the same name.
        """
        container_instance_mock = MagicMock()
        container_instance_mock.__bool__.return_value = True
        container_mock.return_value = container_instance_mock

        docker_client = DockerClient()
        container = docker_client.run_container(
            'test_docker_container_name',
            'test_docker_image_name'
        )
        self.assertEqual(container, container_instance_mock)

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    @patch('rigelcore.clients.docker.DockerClient.get_container')
    def test_docker_run_container_unexistent(self, container_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that the mechanism to run Docker containers works as expected.
        """
        test_name = 'test_docker_container_name'
        test_image = 'test_docker_image_name'
        test_kwargs = {'dummy_key': 'dummy_value'}

        container_instance_mock = MagicMock()
        container_instance_mock.__bool__.return_value = False
        container_mock.return_value = container_instance_mock

        test_container = Mock()
        docker_mock.container.run.return_value = test_container

        docker_client = DockerClient()
        container = docker_client.run_container(
            test_name,
            test_image,
            **test_kwargs
        )

        self.assertEqual(container, test_container)
        docker_mock.container.run.assert_called_once_with(
            test_image,
            name=test_name,
            **test_kwargs
        )

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    @patch('rigelcore.clients.docker.DockerClient.get_container')
    def test_wait_container_status_unexistent(self, container_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that an instance of DockerAPIError is thrown
        if a Docker container to watch does not exist.
        """
        container_instance_mock = MagicMock()
        container_instance_mock.__bool__.return_value = False
        container_mock.return_value = container_instance_mock

        with self.assertRaises(DockerAPIError):
            docker_client = DockerClient()
            docker_client.wait_for_container_status('test_container_name', 'test_status')

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    @patch('rigelcore.clients.docker.DockerClient.get_container')
    @patch('rigelcore.clients.docker.time.sleep')
    def test_wait_container_status_timeout(self, sleep_mock: Mock, container_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that an instance of DockerAPIError is thrown
        if a Docker container to watch does not exist.
        """
        container_instance_mock = MagicMock()
        container_instance_mock.__bool__.return_value = True
        container_mock.return_value = container_instance_mock

        with self.assertRaises(DockerAPIError):
            docker_client = DockerClient()
            docker_client.wait_for_container_status('test_container_name', 'test_status')

    @patch('rigelcore.clients.docker.python_on_whales.docker')
    @patch('rigelcore.clients.docker.DockerClient.get_container')
    @patch('rigelcore.clients.docker.time.sleep')
    def test_wait_container_status_loop(self, sleep_mock: Mock, container_mock: Mock, docker_mock: Mock) -> None:
        """
        Ensure that the mechanism to wait for a given container status value
        to change works as expected.
        """

        test_desired_status = 'test_desired_status'

        container_instance_mock = MagicMock()
        container_instance_mock.__bool__.return_value = True
        container_instance_mock.state.status = 'test_invalid_status'
        container_mock.return_value = container_instance_mock

        def update_container_status(time: int) -> None:
            container_instance_mock.state.status = test_desired_status
        sleep_mock.side_effect = update_container_status

        docker_client = DockerClient()
        docker_client.wait_for_container_status('test_container_name', test_desired_status)
        sleep_mock.assert_called_once_with(docker_client.DOCKER_RUN_WAIT_STATUS)


if __name__ == '__main__':
    unittest.main()
