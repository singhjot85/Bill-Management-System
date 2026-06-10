class NotificationResolverException(Exception):
    pass


class NotificationResolver:
    """
    Resolve out instruction(s) for dispatcher from a given event
    Its responsibilty is to resolve and validate everything before passing to dispatcher.
    If something needs to fetched from databse, resolver should that.
    """

    def resolve(self):
        pass
