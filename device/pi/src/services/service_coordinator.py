from __future__ import annotations
import logging

from typing import Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:  # Pyright workaround
    from .mqtt_service import MqttService
    from .scheduler_service import SchedulerService


logger = logging.getLogger(__name__)

class ServiceCoordinator:
    """
    Coordinates interactions between different services to
    prevent circular dependencies.
    """
    def __init__(self, mqtt_service: MqttService, scheduler_service: SchedulerService):
        self._mqtt_service = mqtt_service
        self._scheduler_service = scheduler_service
    
    def handle_attribute_update_from_mqtt(self, attributes: Dict[str, Any]):
        """
        Called by the MqttService when shared attributes are received.

        Args:
            attributes (Dict[str, Any]): Dictionary of received attributes.
        """
        if "schedule" in attributes:
            try:
                schedule_data = attributes.get("schedule")
                if schedule_data is not None:
                    self._scheduler_service.handle_schedule_attribute_update(schedule_data)
            except Exception as e:
                logger.exception(f"Error notifying SchedulerService of schedule update: {e}")

        # -- Add further attributes we might expect to update here...
 
    def publish_telemetry(self, telemetry_data: Dict[str, Any]):
        """
        Called by other services to request publishing telemetry.

        Args:
            telemetry_data (Dict[str, Any]): A dict of telemetry data to publish.
        """
        try:
            self._mqtt_service.publish_telemetry(telemetry_data)
        except Exception as e:
            logger.error(f"Error requesting telemetry publishing: {e}")

