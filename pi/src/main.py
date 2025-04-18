import functools
import logging
import time
from config.config_handler import ConfigHandler
from config.models.schedule_config import ScheduleConfig
from config.models.system_config import SystemConfig
from rpc import handlers
from services.schedule_service import SchedulerService
from services.thingsboard_mqtt_service import ThingsboardMQTTService

log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)


class App:
    def __init__(self, system_config_path: str = ".sys.cfg", schedule_config_path: str = ".sch.cfg"):
        self.system_config = ConfigHandler(system_config_path, SystemConfig)
        self.schedule_config = ConfigHandler(schedule_config_path, ScheduleConfig)
        self._scheduler = SchedulerService(self.schedule_config)
        
        rpc_handler_map = {
                "updateSchedule": functools.partial(handlers.handle_schedule_update, schedule_config_handler=self.schedule_config, scheduler=self._scheduler)
                }

        self._mqtt = ThingsboardMQTTService(self.system_config.settings.thingsboard_host,
                                            self.system_config.settings.thingsboard_mqtt_port,
                                            self.system_config.settings.thingsboard_token,
                                            rpc_handler_map)


    def run(self):
        self._mqtt.connect()
        while True:
            self._scheduler.run_pending()
            time.sleep(1)

if __name__ == "__main__":
    app = App()
    app.run()

