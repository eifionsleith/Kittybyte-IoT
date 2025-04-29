import logging
import json
import tempfile
import os
from typing import Generic, Type, TypeVar
from typing_extensions import Optional

from pydantic import BaseModel, ValidationError


logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)

class ConfigHandler(Generic[T]):
    """
    Handles application configuration using a JSON file.
    Loands and saves the configuration, validating against the 
    Pydantic model.
    """
    def __init__(self, filepath: str, model: Type[T]):
        """
        Initializes the ConfigHandler.
        
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
        Loads the configuration from the JSON file.
        Validates against the Pydantic model.
        If the file is not found, loading fails or validation fails 
        it attempts to initialize with default values from the model.
        """
        logger.info(f"Attempting to load config from {self._filepath} using model {self._model}")
        data = {}
        file_exists = os.path.exists(self._filepath)
        
        # -- Loading
        if file_exists:
            try:
                with open(self._filepath, 'r') as file:
                    data = json.load(file)
            except json.JSONDecodeError:
                logger.error(f"Malformed config file: {self._filepath}. Using defaults.")
                data = {}
            except Exception as e:
                logger.error(f"Unexpected error reading config file {self._filepath}: {e}. \
                        Using defaults.")
                data = {}

        else:
            logger.warning(f"Configuration file not found: {self._filepath}. Using defaults.")

        # -- Validation
        try:
            self._settings = self._model(**data)
            logger.info(f"Configuration loaded successfully using model {self._model.__name__}.")

            if not file_exists:
                logger.info(f"Saving initial configuration to {self._filepath}.")
                self.save()

        except ValidationError as e:
            logger.error(f"Configuration validation failed for {self._model.__name__}: {e}.\
                    Using defaults.")
            try:
                self._settings = self._model()
            except Exception:
                logger.error(f"Failed to initialize default config for {self._model.__name__}.")
                self._settings = None

    def _get_temp_filepath(self):
        """
        Generates a temporary filepath in the same directory as the config file.
        Used to ensure no partial writes.
        """
        base_dir = os.path.dirname(self._filepath)
        try:
            os.makedirs(base_dir, exist_ok=True)
            fd, temp_path = tempfile.mkstemp(suffix=".tmp", 
                                             prefix=os.path.basename(self._filepath) + "_",
                                             dir=base_dir)
            os.close(fd)
            return temp_path

        except OSError as e:
            logger.error(f"Error creating temporary file in {base_dir}: {e}")
            raise e
        except Exception as e:
            logger.exception(f"An unexpected error occured creating temporary file path in\
                    {base_dir}.")
            raise e

    def save(self):
        """
        Saves the current configuration to the JSON file using a safe write 
        pattern - using a temporary file then renaming it.
        """
        if not self._settings:
            logger.warning("Settings not initialized. Cannot save configuration.")
            return

        try:
            temp_filepath = self._get_temp_filepath()
            json_data = self._settings.model_dump_json(indent=4)

            with open(temp_filepath, 'w') as temp_file:
                temp_file.write(json_data)
                temp_file.flush()
                os.fsync(temp_file.fileno())

            os.replace(temp_filepath, self._filepath)
            logger.info(f"Configuration saved successfully to {self._filepath}.")

        except Exception as e:
            logger.error(f"IOError saving configuration to {self._filepath}.")
            if 'temp_filepath' in locals() and os.path.exists(temp_filepath):
                try:
                    os.remove(temp_filepath)
                except OSError as cleanup_e:
                    logger.error(f"Error clenaing up temporary file {temp_filepath}: {e}")

    def reload(self):
        """
        Reloads the configuration file, discarding current settings.
        """
        logger.info(f"Reloading configuration from {self._filepath}.")
        self._load_config()

    @property
    def settings(self) -> Optional[T]:
        """
        Gets the current configuration settings object.
        Returns None if configuration failed to load.
        """
        return self._settings

    @settings.setter
    def settings(self, value: T):
        """
        Sets the current configuration settings object.
        Does not automatically save the configuration to disk, call .save() after.
        """
        self._settings = value

