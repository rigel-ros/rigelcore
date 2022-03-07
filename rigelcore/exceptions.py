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


class UndeclaredValueError(RigelError):
    """
    Raised whenever an attempt is made to instantiate a class using undeclared field values.

    :type field: string
    :ivar field: The field that was left undeclared.
    """
    base = "Field '{field}' was left undeclared."
    code = 6


class InvalidValueError(RigelError):
    """
    Raised whenever an attempt is made to instantiate a class using invalid field values.

    :type instance_type: Type
    :ivar instance_type: The model being instantiated.
    :type field: string
    :ivar field: The field whose specified value is invalid.
    """
    base = "Unable to create of instance of class '{instance_type}': invalid value for field '{field}'."
    code = 7


class MissingRequiredFieldError(RigelError):
    """
    Raised whenever an attempt is made to instantiate a class with insufficient data.

    :type field: string
    :ivar field: Name of the missing field.
    """
    base = "Required field '{field}' is missing."
    code = 8


class UndeclaredEnvironmentVariableError(RigelError):
    """
    Raised whenever an attempt is made to use the value of an undeclared environment variable.

    :type env: string
    :ivar env: The undeclared environment variable.
    """
    base = "Environment variable {env} is not declared."
    code = 9


class UndeclaredGlobalVariableError(RigelError):
    """
    Raised whenever an undeclared global variable is referenced.

    :type field: string
    :ivar field: Path for the field referencing the global varialble.
    :type var: string
    :ivar var: Global variable identifier.
    """
    base = "Field '{field}' set to have the value of undeclared global variable '{var}'."
    code = 10


class DockerNotFoundError(RigelError):
    """
    Raised whenever an attempt is made to connect to the Docker daemon when it is not running.
    """
    base = "Unable to connect to Docker daemon."
    code = 11


class InvalidDockerClientInstanceError(RigelError):
    """
    Raised whenever an invalid Docker client instance is provided.
    """
    base = "An invalid instance of docker.client.DockerClient was provided."
    code = 12
