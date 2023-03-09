# This class can be used if you want an instrument, but don't have it connected


class DoNothing:
    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, a, b, c, *args, **kwargs):
        pass

    def __getattr__(self, name):
        # Returns none if unknown method
        def method(*args, **kwargs):
            # Return something for getters
            if "get" in name:
                return 1
            else:
                return None

        return method
