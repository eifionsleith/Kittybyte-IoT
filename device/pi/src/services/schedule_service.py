import logging
import schedule

from config.config_handler import ConfigHandler
from config.models.schedule_config import ScheduleConfig, Slot


logger = logging.getLogger(__name__)

# PLACEHOLDER, IMPLEMENT REAL FEEDING LOGIC LATER
def feed(amount):
    logger.info(f"SCHEDULER TASK EXECUTING: Feeding with amount {amount}")

class SchedulerService:
    """
    Handles scheduling of actions to run at predefined times.
    """
    def __init__(self, schedule_config_handler: ConfigHandler[ScheduleConfig]):
        self._schedule_config_handler = schedule_config_handler
        self._day_map = {
                0: schedule.every().monday,
                1: schedule.every().tuesday,
                2: schedule.every().wednesday,
                3: schedule.every().thursday,
                4: schedule.every().friday,
                5: schedule.every().saturday,
                6: schedule.every().sunday
                }
        self.reload()

    def _schedule_feed_slot(self, slot: Slot):
        """Schedules a single feeding action as defined by the config."""
        time_str = slot.time_of_day.strftime("%H:%M")
        try:
            day_schedule = self._day_map.get(slot.day_of_week)
            if day_schedule:
                logger.info(f"Scheduler: Scheduling feeding task for day '{list(self._day_map.keys())[slot.day_of_week]}' at {time_str} with amoutn {slot.amount}")
                day_schedule.at(time_str).do(feed, amount=slot.amount)
            else:
                logger.error(f"Scheduler: Invalid day_of_week '{slot.day_of_week}'. Skipping.")
        except Exception:
            logger.exception(f"Scheduler: Error scheduling feeding task at {time_str} on day {slot.day_of_week}.")

    def reload(self):
        """
        Clears existing jobs, reloads the schedule from the config handler.
        Call if the config changes.
        """
        logger.info("Scheduler: Reloading schedule...")
        schedule.clear()
        config = self._schedule_config_handler.settings
        if config and config.slots:
            logger.info("Scheduler: Loading schedule from config.")
            for slot in config.slots:
                self._schedule_feed_slot(slot)
            logger.info("Scheduler: Schedule reloaded successfully.")
        else:
            logger.warning("Scheduler: No schedule configuration to load.")

    def run_pending(self):
        schedule.run_pending()

