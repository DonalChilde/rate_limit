"""Main module."""
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate is per second.


    """

    def __init__(self, rate, period: timedelta = timedelta(seconds=1)) -> None:
        self.rate = float(rate)
        self.period = period
        self._interval = timedelta(seconds=0)
        self._set_interval()
        self.last_request = datetime.now()
        self.total_delay = timedelta(seconds=0)
        self.total_requests = 0

    def get_delay(self) -> float:
        self.total_requests += 1
        now = datetime.now()
        next_call = self.last_request + self._interval
        if next_call < now:
            delay = timedelta(seconds=0)
        else:
            delay = next_call - now
        self.last_request = next_call
        logger.debug("Issued %s of delay", f"{delay.total_seconds():.3f}")
        self.total_delay += delay
        return delay.total_seconds()

    def adjust_rate(self, change):
        self.rate = float(self.rate + change)
        self._set_interval()

    def adjust_rate_multiplier(self, multiplier):
        self.rate = int(self.rate * multiplier)
        self._set_interval()

    def _set_interval(self):
        try:
            self._interval = timedelta(
                microseconds=(self.period / timedelta(microseconds=1)) / self.rate
            )
            logger.debug("Set interval to %s", self._interval)
        except ZeroDivisionError:
            self._interval = timedelta(seconds=0)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"rate={self.rate!r}, period={self.period!r}"
            ")"
        )
