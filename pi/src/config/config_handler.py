import json
import os
import tempfile
import logging
from typing import Generic, Optional, Type, TypeVar
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)
logger = logging.getLogger(__name__)

class ConfigHandler(Generic[T]):
    """
    Handles application configuration using a JSON file.
    """

    def __init__(self, filepath: str, model: Type[T]):
        """
        Intializes the ConfigHandler.

        Args:
            filepath (str): The path to the configuration JSON file.
            model (Type[BaseModel]): The Pydantic model defining the config structure.
        """
        self._filepath = os.path.abspath(filepath)
        self._model = model
        self._settings: Optional[T] = None
        self._load_config()

    def _load_config(self):
        """
        Loads the configuration from the JSON file specified during
        initialization. Validates against the Pydantic model.
        """
        logger.info(f"Attempting to load config: {self._model}")
        data = {}
        try:
            with open(self._filepath, 'r') as file:
                data = json.load(file)
            logger.debug("Raw data loaded.")

        except FileNotFoundError:
            logger.error("Configuration not found. Using defaults.")

        except json.JSONDecodeError:
            logger.error("Malformed configuration file. Using defaults.")

        except Exception:
            logger.error("Unexpected error loading raw config data. Using defaults.")

        try:
            self._settings = self._model(**data)
            logger.info("Configuration loaded successfully.")

            if not os.path.exists(self._filepath):
                logger.info("Saving initial default configuration.")
                self.save()

        except ValidationError:
            if data: logger.error("Configuration validation failed. Using defaults.")

    def _get_temp_filepath(self):
        """
        Generates a temporary filepath in the same directory.
        """
        base_dir = os.path.dirname(self._filepath)
        try:
            os.makedirs(base_dir, exist_ok=True)  # Directory might not exist on first run.
            fd, temp_path = tempfile.mkstemp(suffix=".tmp", dir=base_dir)
            os.close(fd)
            return temp_path
        
        except OSError as e:
            logger.error("Error creating temporary file.")
            raise e

    def save(self):
        """
        Saves the current configuration to the JSON file.
        """
        if not self._settings:
            logger.error("Settings not initialized, cannot save.")
            return

        try:
            temp_filepath = self._get_temp_filepath()
            logger.debug(f"Saving configuration to temporary file: {temp_filepath}")
            json_data = self._settings.model_dump_json(indent=4)

            with open(temp_filepath, 'w') as file:
                file.write(json_data)
                file.flush()
                os.fsync(file.fileno())

            os.replace(temp_filepath, self._filepath)
            logger.info("Configuration saved successfully.")
        
        except IOError as e:
            logger.error(f"IOError saving configuration: {e}")

        except Exception as e:
            logger.error("Unknown error saving configuration: {e}")

    def reload(self):
        """
        Reloads the configuration from the file.
        """
        self._load_config()
    
    @property
    def settings(self) -> Optional[T]:
        return self._settings

    @settings.setter
    def settings(self, value: T):
        self._settings = value

