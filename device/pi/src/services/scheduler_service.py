import logging
from threading import Timer
from typing import Optional

from ..config.config_handler import ConfigHandler


logger = logging.getLogger(__name__)

# -- Cat Detection State --
## Used to prevent double dispensing, set True on a 
## scheudled dispense operation, set False on the next 
## cat detection event.
dispensing_locked = False
## Used to start a timer after we dispense, that can 
## then alert the user if their cat didn't eat.
missed_feed_timer: Optional[Timer] = None

DEFAULT_MISSED_FEED_TIMER_MINUTES = 30
DEFAULT_MISSED_FEED_TIMER_SECONDS = DEFAULT_MISSED_FEED_TIMER_MINUTES * 60

class SchedulerService:
    """
    Handles scheduling of feeding actions to run at predefined
    times based on the ScheduleConfig.

    This includes dispensing food, locking future dispensing and
    alerting of missed feeding events.
    """
    def __init__(self, schedule_config_handler: ConfigHandler):
        ...
        # TODO: This.
