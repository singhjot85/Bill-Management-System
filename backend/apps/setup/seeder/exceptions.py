class SeederException(Exception):
    """General exception raised by seeder components."""

    pass


class ObjectCreationException(SeederException):
    """Raised when an error occurs during object creation."""

    pass
