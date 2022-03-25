import functools


class NotConnectedError(RuntimeError):
    pass


def ensure_connected(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        # requires isinstance(args[0], Device)
        if not args[0].is_connected:
            raise NotConnectedError
        return fn(*args, **kwargs)

    return wrapper
