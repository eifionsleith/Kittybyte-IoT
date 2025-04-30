import logging
import time

from config.config_handler import ConfigHandler 
from config.models.schedule_config import ScheduleConfig
from communication.arduino_service import ArduinoService
from services.service_coordinator import ServiceCoordinator
from services.mqtt_service import MqttService
from services.scheduler_service import SchedulerService
from services.detection_service import CatDetectionService

log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)
logger = logging.getLogger(__name__)

#-- Configuration
SCHEDULE_CONFIG_PATH = "config/schedule.json"
#--

class App:
    """
    The main App class, containing the main loop and coordinating
    logic between services.
    """
    def __init__(self):
        """
        Initializes application services.
        """
        # -- Config Handlers
        self._schedule_config_handler = ConfigHandler[ScheduleConfig](
                SCHEDULE_CONFIG_PATH,
                model=ScheduleConfig
                )

        # -- Allows services to intercommunicate
        # TODO: Move the hardcoded variables to a configuration file.
        self._service_coordinator = ServiceCoordinator()

        self._arduino_service = ArduinoService("/dev/ttyACM0", 9600)

        self._mqtt_service = MqttService(
                host="192.168.0.17",
                port=1883,
                token="mi79zwGei1yakoM5F1OM",
                rpc_map={},
                coordinator=self._service_coordinator
                )

        self._scheduler_service = SchedulerService(
                self._schedule_config_handler,
                coordinator=self._service_coordinator
                )

        self._detection_service = CatDetectionService()

        self._service_coordinator.set_services(self._mqtt_service, self._scheduler_service)
        logger.info("Application services initialized.")

    def run(self):
        """
        Runs the main application loop.
        """
        self._arduino_service.connect()
        self._mqtt_service.connect()

        try:
            while True:
                # -- Process the data regarding the Arduino
                self._arduino_service.process_incoming_data()
                self._arduino_service.cleanup_pending_commands(60)  # TODO: Assign a timeout for commands individually
                
                # -- Run pending scheduled tasks
                self._scheduler_service.run_pending()

                # -- Process frames for the detection service, if it's running 
                # Will automatically handle the case where it is not running.
                self._detection_service.capture_and_process_frame()

                time.sleep(0.01)

        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt received, shutting down.")
        except Exception:
            logger.exception("An unhandled exception occured in the main loop, shutting down.")

        finally:
            self.shutdown()

    def shutdown(self):
        """
        Shuts down the application, cleaning up services.
        """
        logger.info("Cleaning up application services...")
        if self._detection_service is not None:
            self._detection_service.stop()
        if self._mqtt_service is not None:
            self._mqtt_service.disconnect()
        if self._arduino_service is not None:
            self._arduino_service.disconnect()
        logger.info("Application shutdown complete.")

if __name__ == "__main__":
    app = App()
    app.run()

