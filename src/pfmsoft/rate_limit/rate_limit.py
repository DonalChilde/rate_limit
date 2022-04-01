"""Main module."""

import logging
from asyncio import sleep as async_sleep
from datetime import datetime, timedelta
from enum import Enum, auto
from time import perf_counter_ns, sleep
from typing import Any, Callable

logger = logging.getLogger(__name__)


class IntervalDeltaType(Enum):
    """Defined types of interval change."""

    SECONDS = auto()
    PERCENTAGE = auto()


class RateLimit:
    """
    Base class and factory for RateLimit subclasses

    RateLimit allows a guaranteed maximum rate of function calls over time.
    When RateLimit is used as a contextmanager, it will return the appropriate
    synchronous or async subclass.
    """

    def __init__(self, limit_interval: int):
        self.limit_interval: int = limit_interval
        self.last_called: int = 0
        self.total_delay: int = 0
        self.total_requests: int = 0

    def __aenter__(self) -> "AsyncRateLimit":
        return AsyncRateLimit(limit_interval=self.limit_interval)

    def __aexit__(self, exc_type, exc_value, exc_traceback):
        pass

    def __enter__(self) -> "SyncRateLimit":
        return SyncRateLimit(limit_interval=self.limit_interval)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass

    def increase_interval_percentage(self, delta: float):
        """
        Increase the interval between limit calls by a percentage of the current limit.

        Args:
            delta: The percentage change, should be expressed as a float, e.g. 25% == 0.25
        """
        self.set_interval(int(self.limit_interval * (1 + delta)))

    def increase_interval(self, delta: int):
        """
        Increase the interval between limit calls by a fixed amount.

        Args:
            delta:  The amount of increase in nanoseconds.
        """

        self.set_interval(self.limit_interval + delta)

    def decrease_interval_percentage(self, delta: float):
        """
        Decrease the interval between limit calls by a percentage of the current limit.

        Args:
            delta: The percentage change, should be expressed as a float, e.g. 25% == 0.25
        """
        self.set_interval(int(self.limit_interval * (1 - delta)))

    def decrease_interval(self, delta: int):
        """
        Decrease the interval between limit calls by a fixed amount.

        Args:
            delta:  The amount of decrease in nanoseconds.
        """

        self.set_interval(self.limit_interval - delta)

    def set_interval(self, interval: int):
        """
        Set the limit interval.

        Ensures the limit interval is not less than 0.

        Args:
            interval: The interval in nanoseconds.
        """
        if self.limit_interval <= 0:
            self.limit_interval = 0
            return
        self.limit_interval = interval

    def check_for_wait(self) -> int:
        """
        Check to see if there is time remaining before next limit call.

        Returns:
            The remaining time in nanoseconds, returns zero if no wait required.
        """
        since_last_called = perf_counter_ns() - self.last_called
        if since_last_called >= self.limit_interval:
            return 0
        wait = self.limit_interval - since_last_called
        self.total_delay += wait
        self.total_requests += 1
        return wait

    def _update_last_called(self):
        self.last_called = perf_counter_ns()

    @staticmethod
    def seconds_to_nanoseconds(seconds: float) -> int:
        """Convert seconds to nanoseconds"""
        nanos = int(seconds * 1000000000)
        return nanos

    @staticmethod
    def nanoseconds_to_seconds(nanos: int) -> float:
        """
        Convert nanoseconds to seconds

        Args:
            nanos: Nanoseconds to convert.

        Returns:
            Seconds as a float.
        """
        seconds = nanos / 1000000000
        return seconds

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(limit_interval={self.limit_interval!r})"

    def __str__(self) -> str:
        pass
        # TODO make a good str rep


class AsyncRateLimit(RateLimit):
    """
    An async RateLimit.

    Examples go here


    """

    async def limit(self, func: Callable, *args, **kwargs) -> Any:
        """
        Ensure an async function call does not exceed the rate limit.

        _extended_summary_

        Args:
            func: The function to be limited
            *args: Arguments passed to the function when called.
            **kwargs: Keyword arguments pass to the function when called.

        Returns:
            The return value of func, if any.
        """
        await self._respect_limit()
        result = await func(*args, **kwargs)
        self._update_last_called()
        return result

    async def _respect_limit(self):
        await async_sleep(self.nanoseconds_to_seconds(self.check_for_wait()))


class SyncRateLimit(RateLimit):
    """
    A synchronous RateLimit.

    Examples go here


    """

    def limit(self, func: Callable, *args, **kwargs) -> Any:
        """
        Ensure a function call does not exceed the rate limit.

        _extended_summary_

        Args:
            func: The function to be limited
            *args: Arguments passed to the function when called.
            **kwargs: Keyword arguments pass to the function when called.

        Returns:
            The return value of func, if any.
        """
        self._respect_limit()
        result = func(*args, **kwargs)
        self._update_last_called()
        return result

    def _respect_limit(self):
        sleep(self.nanoseconds_to_seconds(self.check_for_wait()))


# class RateLimiter:
#     """
#     Rate is per second.


#     """

#     def __init__(self, rate, period: timedelta = timedelta(seconds=1)) -> None:
#         self.rate = float(rate)
#         self.period = period
#         self._interval = timedelta(seconds=0)
#         self._set_interval()
#         self.last_request = datetime.now()
#         self.total_delay = timedelta(seconds=0)
#         self.total_requests = 0

#     def get_delay(self) -> float:
#         self.total_requests += 1
#         now = datetime.now()
#         next_call = self.last_request + self._interval
#         if next_call < now:
#             delay = timedelta(seconds=0)
#         else:
#             delay = next_call - now
#         self.last_request = next_call
#         logger.debug("Issued %s of delay", f"{delay.total_seconds():.3f}")
#         self.total_delay += delay
#         return delay.total_seconds()

#     def adjust_rate(self, change):
#         self.rate = float(self.rate + change)
#         self._set_interval()

#     def adjust_rate_multiplier(self, multiplier):
#         self.rate = int(self.rate * multiplier)
#         self._set_interval()

#     def _set_interval(self):
#         try:
#             self._interval = timedelta(
#                 microseconds=(self.period / timedelta(microseconds=1)) / self.rate
#             )
#             logger.debug("Set interval to %s", self._interval)
#         except ZeroDivisionError:
#             self._interval = timedelta(seconds=0)

#     def __repr__(self) -> str:
#         return (
#             f"{self.__class__.__name__}("
#             f"rate={self.rate!r}, period={self.period!r}"
#             ")"
#         )
