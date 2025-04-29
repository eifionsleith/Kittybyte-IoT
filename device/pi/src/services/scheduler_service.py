from functools import partial
import logging
import schedule
from threading import Timer
from typing import Optional

from .mqtt_service import MqttService
from ..config.config_handler import ConfigHandler
from ..config.models.schedule_config import Slot


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
    def __init__(self, schedule_config_handler: ConfigHandler, mqtt_service: MqttService):
        """
        Initializes the SchedulerService

        Args:
            schedule_config_handler (ConfigHandler[ScheduleConfig]):
                Handler for the schedule configuration.
            mqtt_service (MqttService):
            The MQTT service instance for backend communication.
        """
        self._schedule_config_handler = schedule_config_handler
        self._mqtt_service = mqtt_service

        # Mapping of the integer day representation
        # to the one used by the schedule library.
        self._day_map = {
                0: schedule.every().monday,
                1: schedule.every().tuesday,
                2: schedule.every().wednesday,
                3: schedule.every().thursday,
                4: schedule.every().friday,
                5: schedule.every().saturday,
                6: schedule.every().sunday
                }

        global dispensing_locked, missed_feed_timer
        dispensing_locked = False
        missed_feed_timer = None
        self.reload_schedule()

    def reload_schedule(self):
        """
        Clears existing jobs and reloads the schedule using the 
        config handler. Must be called when the schedule changes.
        """
        logger.info("Reloading schedule...")
        schedule.clear()
        config = self._schedule_config_handler.settings
        if config and config.slots:
            logger.info(f"Loading {len(config.slots)} from config.")
            for slot in config.slots:
                self._schedule_feed_slot(slot)
            logger.info("Schedule reloaded successfully.")
        else:
            logger.warning("No schedule configuration to load.")

    def _schedule_feed_slot(self, slot: Slot):
        """
        Schedules a single feeding action as defined by the config slot.
        """
        time_str = slot.time_of_day.strftime("%H:%M")  # schedule needs string format
        day_of_week = slot.day_of_week

        try:
            day_schedule = self._day_map.get(day_of_week)
            if day_schedule:
                job_func = partial(self._trigger_scheduled_feed, amount=slot.amount)
                day_schedule.at(time_str).do(job_func)
            else:
                logger.error(f"Invalid day_of_week '{day_of_week}'. Skipping slot.")
        except Exception:
            logger.exception("Error scheduling feeding task for day {day_of_week} at {time_str}.")

    def _trigger_scheduled_feed(self, amount: int):
        """
        Called by the schedule library when a feeding time arrives.

        Initiates the feeding sequence, locks dispensing and starts 
        the missed feed timer.

        Args:
            amount (int): Amount of food to dispense, in grams.
        """
        logger.info("Scheduled feeding event arrives, triggering feeding sequence.")
        ...  # TODO

    def _missed_feed_alert(self):
        """
        Called by the timer if a cat is not detected within the 
        DEFAULT_MISSED_FEED_TIMER_MINUTES duration after the last
        feeding event. Send an alert to Thingsboard to notify 
        the user.
        """
        logger.info("Missed feeding alert trigger.")
        ...  # TODO

    def notify_cat_detected(self):
        """
        To be called by the cat detection system when a cat is 
        detected. Unlocks dispensing if currently locked, and 
        cancels the missed feed timer.

        Safe to be called repeatedly if cats are detected more
        than once.
        """
        logger.info("notify_cat_detected called.")
        ...  # TODO

    def is_dispensing_locked(self) -> bool:
        """
        Returns the current state of the dispensing lock.
        """
        return dispensing_locked

    def run_pending(self):
        """
        Runs all pending jobs that are scheduled to run.

        To be called in the main loop.
        """
        schedule.run_pending()

