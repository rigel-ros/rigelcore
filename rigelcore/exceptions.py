from typing import Type, Union


class RigelError(Exception):
    """
    The base exception class for all Rigel errors.

    :type base: string
    :var base: The error message.
    :type code: int
    :cvar code: The error code.
    """
    base: str = 'Undefined Rigel error.'
    code: int = 1

    def __init__(self, **kwargs: Union[str, int, float, Type]):
        Exception.__init__(self, self.base.format(**kwargs))
        self.kwargs = kwargs


class InvalidDockerImageNameError(RigelError):
    """
    Raised whenever an attempt is made to tag a Docker image using an invalid image name.

    :type image: string
    :ivar image: Invalid Docker image name.
    """
    base = "Invalid Docker image name '{image}'."
    code = 2


class DockerImageNotFoundError(RigelError):
    """
    Raised whenever an attempt is made to tag a Docker image that does not exist.

    :type image: string
    :ivar image: Name of unexisting Docker image.
    """
    base = "Docker image {image} was not found."
    code = 3


class InvalidImageRegistryError(RigelError):
    """
    Raised whenever an attempt is made to authenticate with an invalid Docker registry.

    :type registry: string
    :ivar registry: Name of invalid Docke registry.
    """
    base = "Invalid Docker registry '{registry}'."
    code = 4


class DockerOperationError(RigelError):
    """
    Raised whenever an error occurs while calling the Docker API.

    :type msg: string
    :ivar msg: The error message as provided by the Docker API.
    """
    base = "An error while calling Docker: {msg}."
    code = 5
