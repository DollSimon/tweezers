class lazy(object):
    """
    Property for the lazy evaluation of Python attributes. In the example below, the ``expensive_computation()`` is only
    called when the attribute ``object.my_attribute`` is accessed for the first time.

    Example:
        Use the ``@lazy`` decorator for a function that returns the result of the computation. Access it as a normal
        attribute::

            @lazy
            def my_attribute(self):
                value = self.expensive_computation()
                return value
    """

    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        if instance is None:
            return None
        value = self.func(instance)
        setattr(instance, self.func.__name__, value)
        return value