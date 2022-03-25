"""Top-level entry-point for the <project_name> package"""

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version("pupil-core-network-client")
except PackageNotFoundError:
    # package is not installed
    __version__ = None

from .decorators import NotConnectedError
from .device import ClockFunction, ClockOffsetStatistics, Device
from .subscription import BackgroundSubscription, Message, Subscription

__all__ = [
    "__version__",
    "ClockFunction",
    "ClockOffsetStatistics",
    "Device",
    "Message",
    "NotConnectedError",
    "Subscription",
    "BackgroundSubscription",
]
