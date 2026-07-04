# Seeder Custom Exceptions


class SeederRunException(Exception):
    """Exception raised at seeder run level."""

    pass


class SeederException(Exception):
    """General exception raised by seeder components."""

    pass


class ObjectCreationException(SeederException):
    """Raised when an error occurs during object creation."""

    pass
