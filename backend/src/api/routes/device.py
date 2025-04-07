from uuid import UUID
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from tb_rest_client import RestClientCE

from api.dependencies import get_config, get_current_superuser_from_jwt, get_current_user, get_db, get_thingsboard_client
from crud.device import device_crud_interface
from models.user import User
from schema.device import DeviceCreate, DeviceOutput
from utils.config import AppConfig
from utils.thingsboard.thingsboard_exceptions import DeviceProvisioningException, ThingsboardNotFoundException
from utils.thingsboard.thingsboard_models import DeviceCredentials
from utils.thingsboard.utils import ThingsboardUtils


router = APIRouter()

@router.post("/", response_model=DeviceOutput, dependencies=[Depends(get_current_superuser_from_jwt)])
def create_device(db: Annotated[Session, Depends(get_db)]):
    """
    Creates a new device in the local database and Thingsboard.

    Only available to superusers.
    """ 
    device = device_crud_interface.create(db, DeviceCreate())

    ##! Logic to be handled by provisioning.
    # thingsboard_device = ThingsboardUtils.create_device(thingsboard_client, str(device.id), UUID("94b61ab0-0ff2-11f0-a42f-ddf6a090e9e6"))
    # if thingsboard_device.id is None:
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #                         detail="Failed to create device in thingsboard.")
    #
    # thingsboard_device_id = UUID(thingsboard_device.id.id)
    # device = device_crud_interface.set_thingsboard_id(db, device, thingsboard_device_id)
    
    return device

@router.post("/{device_id}/provision", response_model=DeviceCredentials)
def provision_device(db: Annotated[Session, Depends(get_db)],
                     current_user: Annotated[User, Depends(get_current_user)],
                     thingsboard_client: Annotated[RestClientCE, Depends(get_thingsboard_client)],
                     config: Annotated[AppConfig, Depends(get_config)],
                     device_id: UUID):
    """
    Provisions a device within Thingsboard, using the local Device ID.

    Assigns the device to the currently authenticated user, provisions and 
    creates the device in Thingsboard, requesting credentials, then links
    this Thingsboard instance to the local database instance before returning
    the device authentication token - to be used by the device to communicate 
    via MQTT.
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
                                                        config.thingsboard.provisioning.key,
                                                        config.thingsboard.provisioning.secret)
        thingsboard_device_id = ThingsboardUtils.get_device_id_by_name(thingsboard_client, str(device.id))

    except (DeviceProvisioningException, ThingsboardNotFoundException, ValueError):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Device provisioning failed.")
    
    device = device_crud_interface.set_thingsboard_id(db, device, thingsboard_device_id)
    device = device_crud_interface.set_provisioned_at(db, device)
    device = device_crud_interface.set_owner(db, device, current_user)

    return credentials

##! TODO: Work in progress!
@router.post("/{device_id}/dispense")
def dispense(db: Annotated[Session, Depends(get_db)],
             current_user: Annotated[User, Depends(get_current_user)],
             thingsboard_client: Annotated[RestClientCE, Depends(get_thingsboard_client)],
             device_id: UUID,
             dispense_amount: int):
    """
    Sends a MQTT message triggering a dispense action on the device,
    assuming the authenticated user is the device's owner.
    """

    device = device_crud_interface.get_by_id(db, device_id)
    thingsboard_device_id = device.thingsboard_id
    dispense_command = {
            "method": "dispense",
            "params": {
                "amount": dispense_amount
                }
            }
    print("Trying to send request...")
    response = thingsboard_client.handle_two_way_device_rpc_request(str(thingsboard_device_id), dispense_command)
    print(response)

