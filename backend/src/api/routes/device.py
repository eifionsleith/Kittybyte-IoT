from typing import Annotated, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from tb_rest_client import RestClientCE

from src.api.dependencies import get_current_superuser, get_current_user, get_db, get_settings, get_tb_client
from src.crud.device import device_crud_interface
from src.models.user import User
from src.schemas.devices import DeviceCreate, DeviceOut, DeviceUserUpdate, DeviceUpdate
from src.schemas.misc import Success
from src.utils.config import AppSettings
from src.utils.thingsboard.thingsboard_utils import DeviceCredentials, DeviceProvisioningException, ThingsboardBadResponseException, ThingsboardNotFoundException, ThingsboardUtils


router = APIRouter()

@router.post("/", response_model=DeviceOut, dependencies=[Depends(get_current_superuser)], status_code=201)
def create_device(db: Annotated[Session, Depends(get_db)],
                  ) -> DeviceOut:
    """
    Allows a superuser to create a new device, with auto-generated UUID.

    This is to be provisioned later, adding it to Thingsboard and generating
    access credentials.
    """
    device = device_crud_interface.create(db, DeviceCreate())
    return device

@router.get("/")
def get_my_devices(db: Annotated[Session, Depends(get_db)],
                   current_user: Annotated[User, Depends(get_current_user)]
                   ) -> List[DeviceOut]:
    """
    Gets a list of all the current users devices.
    """
    devices = device_crud_interface.get_devices_with_owner(db, current_user.id)
    return [DeviceOut.model_validate(device) for device in devices]

@router.put("/{device_id}", response_model=DeviceOut)
def update_device(db: Annotated[Session, Depends(get_db)],
                  current_user: Annotated[User, Depends(get_current_user)],
                  device_update: DeviceUserUpdate,
                  device_id: UUID
                  ) -> DeviceOut:
    """
    Allows the current user to update the mutable fields of
    their owned device.
    """
    device = device_crud_interface.get_by_id(db, device_id)
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Device not found.")

    if device.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="User can't do this.")

    device_update_data = device_update.model_dump(exclude_unset=True)
    device = device_crud_interface.update(db, device, DeviceUpdate(**device_update_data))
    return device

# TODO: Doesn't handle devices that have been unregistered.
@router.post("/{device_id}/register", response_model=DeviceCredentials)
def register_and_provision_device(db: Annotated[Session, Depends(get_db)],
                                  current_user: Annotated[User, Depends(get_current_user)],
                                  thingsboard_client: Annotated[RestClientCE, Depends(get_tb_client)],
                                  settings: Annotated[AppSettings, Depends(get_settings)],
                                  device_id: UUID
                                  ) -> DeviceCredentials:
    """
    Provisions and then registers a device within Thingsboard, using
    the local device ID to look as Thingsboard device name.

    Returns a device authentication token to be used during MQTT
    communication.
    """
    device = device_crud_interface.get_by_id(db, device_id)
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Device not found.")

    if device.provisioned_at is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Device already provisioned.")

    try:
        credentials = ThingsboardUtils.provision_device(thingsboard_client,
                                                        str(device.id),
                                                        settings.thingsboard.provisioning.key,
                                                        settings.thingsboard.provisioning.secret)
        thingsboard_device_id = ThingsboardUtils.get_device_id_by_name(thingsboard_client, str(device.id))
        device = device_crud_interface.update(db, device, DeviceUpdate(thingsboard_id=thingsboard_device_id,
                                                                       owner_id=current_user.id))
        device = device_crud_interface.set_is_provisioned(db, device)
        return credentials

    except (DeviceProvisioningException, ThingsboardNotFoundException, ThingsboardBadResponseException):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Device provisioning failed.")

@router.post("/{device_id}/unregister", response_model=Success)
def unregister_device(db: Annotated[Session, Depends(get_db)],
                      current_user: Annotated[User, Depends(get_current_user)],
                      device_id: UUID
                      ) -> Success:
    """
    Unregisters a device from the current user, allowing the device
    to then be registered once more by another user.
    """
    device = device_crud_interface.get_by_id(db, device_id)
    if device is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Device not found.")

    if device.owner_id is not current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="User can't do this.")

    fields_to_update = DeviceUpdate(owner_id=None)
    device = device_crud_interface.update(db, device, fields_to_update)
    return Success(message="Device unregistered")

