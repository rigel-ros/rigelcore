import docker
import time
from rigelcore.exceptions import (
    DockerAPIError,
    DockerOperationError,
    InvalidDockerClientInstanceError,
    InvalidDockerImageNameError,
)
from rigelcore.loggers import DockerLogPrinter, MessageLogger
from typing import Any, Dict, Optional


class DockerClient:
    """
    A wrapper class for the docker.client.DockerClient.
    Keeps the same functionality but allows for error handling that suits better Rigel.
    """

    DOCKER_CONTAINER_ID_DISPLAY_SIZE: int = 12
    DOCKER_RUN_TIMEOUT: int = 120  # seconds
    DOCKER_RUN_WAIT_STATUS: int = 3  # seconds

    # A Docker client instance.
    client: docker.client.DockerClient

    def __init__(self, client: Optional[docker.client.DockerClient] = None) -> None:
        """
        Create a Docker client instance.

        :type client: Optioanl[docker.client.DockerClient]
        :param client: A Docker client instance.
        """
        if client:
            if not isinstance(client, docker.client.DockerClient):
                raise InvalidDockerClientInstanceError()
            self.client = client
        else:
            try:
                self.client = docker.from_env()
            except docker.errors.DockerException as exception:
                raise DockerAPIError(exception=exception)

    def print_logs(self, image: docker.models.images.Image) -> None:
        """
        Display Docker log messages for a given Docker image.

        :type image: docker.models.images.Image
        :param image: The Docker image.
        """
        printer = DockerLogPrinter()

        iterator = iter(image)
        while True:
            try:
                log = next(iterator)
                printer.log(log)
            except StopIteration:  # no more log messages
                if 'error' in log:
                    raise DockerOperationError(msg=log['error'])
                break

    def login(self, registry: str, username: str, password: str) -> None:
        """
        Authenticate user with a given Docker image regisry.

        :type registry: string
        :param registry: The registry to authenticate with.
        :type username: string
        :param username: The registry username.
        :type password: string
        :param password: The registry password.
        """
        try:
            self.client.api.login(
                username=username,
                password=password,
                registry=registry
            )
        except docker.errors.DockerException as exception:
            raise DockerAPIError(exception=exception)

    def get_image(self, name: str) -> Optional[docker.models.images.Image]:
        """
        Get an existing Docker image.

        :type name: string
        :param name: The Docker image name.
        :rtype: Optional[docker.models.images.Image]
        :return: The Docker image if existent. None otherwise.
        """
        try:
            image = self.client.images.get(name)
            return image
        except docker.errors.ImageNotFound:  # Docker images does not exist locally
            return None
        except docker.errors.DockerException as exception:
            raise DockerAPIError(exception=exception)

    def build_image(self, path: str, dockerfile: str, image: str, buildargs: Dict[str, str]) -> None:
        """
        Build a new Docker image.

        :type path: string
        :param path: Root of the build context.
        :type dockerfile: string
        :param dockerfile: Path for the Dockerfile.
        :type image: string
        :param image: The name for the new Docker image.
        :type buildargs: Dict[str, str]
        :param buildargs: Build arguments.
        """
        try:
            built_image = self.client.api.build(
                path=path,
                dockerfile=dockerfile,
                tag=image,
                buildargs=buildargs,
                decode=True,
                rm=True
            )
            self.print_logs(built_image)
        except docker.errors.DockerException as exception:
            raise DockerAPIError(exception=exception)

    def tag_image(self, source_image: str, target_image: str) -> None:
        """
        Create a Docker image that references an existing Docker image.

        :type source_image: string
        :param source_image: The name of the image being referenced.
        :type target_image: string
        :param target_image: The desired name for the new image.
        """
        if ':' in target_image:
            try:
                desired_image_name, desired_image_tag = target_image.split(':')
            except ValueError:
                raise InvalidDockerImageNameError(image=target_image)
        else:
            desired_image_name = target_image
            desired_image_tag = 'latest'

        try:
            self.client.api.tag(
                image=source_image,
                repository=desired_image_name,
                tag=desired_image_tag
            )
        except docker.errors.DockerException as exception:
            raise DockerAPIError(exception=exception)

    def push_image(self, image: str) -> None:
        """
        Push a Docker image to a Docker image registry.

        :type image: string
        :param image: The name of the Docker image.
        """
        try:
            pushed_image = self.client.api.push(image, stream=True, decode=True)
            self.print_logs(pushed_image)
        except docker.errors.DockerException as exception:
            raise DockerAPIError(exception=exception)

    def get_network(self, name: str) -> Optional[docker.models.networks.Network]:
        """
        Get a Docker network.

        :type name: string
        :param name: The name of the Docker network.

        :rtype: Optional[docker.models.networks.Network]
        :return: The Docker network with the specified name.
        """
        try:
            listing = self.client.networks.list(names=[name])
            if listing:
                return listing[0]
            return None
        except docker.errors.DockerException as exception:
            raise DockerAPIError(exception=exception)

    def create_network(self, name: str, driver: str) -> docker.models.networks.Network:
        """
        Create a Docker network.

        :type name: string
        :param name: The name of the Docker network.
        :type driver: string
        :param driver: Name of driver used to create the network.

        :rtype: docker.models.networks.Network
        :return: The Docker network with the specified name.
        """
        network = self.get_network(name)
        if not network:
            try:
                return self.client.networks.create(name, driver=driver)
            except docker.errors.DockerException as exception:
                raise DockerAPIError(exception=exception)
        return network  # return already existing network

    def remove_network(self, name: str) -> None:
        """
        Remove a Docker network.

        :type name: string
        :param name: The name of the Docker network.
        """
        network = self.get_network(name)
        if network:
            try:
                network.remove()
            except docker.errors.DockerException as exception:
                raise DockerAPIError(exception=exception)

    def get_container(self, name: str) -> Optional[docker.models.containers.Container]:
        """
        Get a Docker container.

        :type name: string
        :param name: The name of the Docker container.

        :rtype: Optional[docker.models.containers.Container]
        :return: The Docker container with the specified name.
        """
        try:
            listing = self.client.containers.list(filters={'name': name})
            if listing:
                return listing[0]
            return None
        except docker.errors.DockerException as exception:
            raise DockerAPIError(exception=exception)

    def run_container(
        self,
        name: str,
        image: str,
        **kwargs: Any
    ) -> docker.models.containers.Container:
        """
        Run a Docker container with a given name.

        :type name: string
        :param name: The Docker container name.
        :type image: string
        :param name: The Docker image.
        :type kwargs: Dict[str, Any]
        :param kwargs: Keyword arguments for the Docker API. Consult the Docker SDK for Python
        documentation for more information (https://docker-py.readthedocs.io/en/stable/containers.html)

        :rtype: docker.models.containers.Container
        :return: The created Docker container
        """
        container = self.get_container(name)
        if not container:
            kwargs['name'] = name
            try:
                return self.client.containers.run(image, **kwargs)
            except docker.errors.DockerException as exception:
                raise DockerAPIError(exception=exception)
        return container  # return already existing container

    def remove_container(self, name: str) -> None:
        """
        Remove a Docker container.

        :type name: string
        :param name: The name of the Docker container.
        """
        container = self.get_container(name)
        if container:
            try:
                container.remove(v=True, force=True)
            except docker.errors.DockerException as exception:
                raise DockerAPIError(exception=exception)

    def wait_for_container_status(
            self,
            name: str,
            status: str
            ) -> None:
        """
        Wait for a container status to change to a desired value.

        :type name: string
        :param name: The name of the container to watch.
        :type status: string
        :param status: The desires container status.
        """
        logger = MessageLogger()

        elapsed_time = 0  # seconds
        while True:
            container = self.get_container(name)
            if container:
                if elapsed_time < self.DOCKER_RUN_TIMEOUT:
                    if container.status == status:
                        return
                    time.sleep(self.DOCKER_RUN_WAIT_STATUS)
                    elapsed_time = elapsed_time + self.DOCKER_RUN_WAIT_STATUS
                    logger.warning('Waiting for status of container {} to become "{}". Current status is "{}".'.format(
                        container.id[:self.DOCKER_CONTAINER_ID_DISPLAY_SIZE],
                        status,
                        container.status
                    ))
                else:
                    raise DockerAPIError(exception=docker.errors.DockerException(
                        'Timeout while waiting for status of container {} to become "{}".'.format(
                            container.id[:self.DOCKER_CONTAINER_ID_DISPLAY_SIZE],
                            status
                        )
                    ))
            else:
                raise DockerAPIError(exception=docker.errors.DockerException(
                    f'Unable to watch over status of container "{name}" since it does not exist.'
                ))
