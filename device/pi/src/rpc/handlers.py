import logging
from config.config_handler import ConfigHandler
from config.models.schedule_config import ScheduleConfig
from services.schedule_service import SchedulerService

logger = logging.getLogger(__name__)

def handle_schedule_update(rpc_params: dict, schedule_config_handler: ConfigHandler, scheduler: SchedulerService):
    """
    Handles the 'updateSchedule' rpc command, writing
    the new schedule to the configuration.
    """
    logger.info("RPC: Executing update schedule.")
    new_schedule = ScheduleConfig(**rpc_params)
    schedule_config_handler.settings = new_schedule
    schedule_config_handler.save()
    scheduler.reload()
    return {"status": "success", "message": "Schedule updated successfully."}

