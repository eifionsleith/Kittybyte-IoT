"""
Devices:
    register (POST): Register a device with provided ID to user with ID. 
        If the device doesn't exist I suppose it makes sense to create in the database.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import paho.mqtt.publish as publish

from api.v0.dependencies.auth import get_user_from_jwt
from api.v0.dependencies.database import get_db
from models.device import Device
from models.user import User
from crud.device import device_crud_interface
from schema.device import DeviceUpdate, DeviceCreate
from utils.mqtt import publish_single

router = APIRouter()

@router.post("/{device_id}/register")
def register_device_to_user(
        db: Annotated[Session, Depends(get_db)],
        current_user: Annotated[User, Depends(get_user_from_jwt)],
        device_id: int):
    """
    Registers a device with given ID to a given user, if device doesn't already exist
    add it to the database.
    """
    device = device_crud_interface.get_one(db, Device.id == device_id)
    if device is None:
        device_database_object = DeviceCreate(
                id=device_id,
                owner_id=current_user.id)
        device = device_crud_interface.create(db, device_database_object)
        return device

    if device.owner_id is None:
        device = device_crud_interface.update(db, device, DeviceUpdate(owner_id=current_user.id))
        return device
    
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Device already has an owner.")

@router.delete("/{device_id}/unregister")
def unregister_device(
        db: Annotated[Session, Depends(get_db)],
        current_user: Annotated[User, Depends(get_user_from_jwt)],
        device_id: int):
    """
    Unregisters a device from the system, if the current user is its owner.
    """
    device = device_crud_interface.get_one(db, Device.id == device_id)
    if device is None:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No such device.")

    if device.owner_id != current_user.id:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User lacks permissions to modify this device.")

    device_update = DeviceUpdate(name=None, owner_id=None)
    device_crud_interface.update(db, device, device_update)
    return {"message": "Device unregistered successfully."}

@router.post("/{device_id}/dispense")
def dispense(
        db: Annotated[Session, Depends(get_db)],
        current_user: Annotated[User, Depends(get_user_from_jwt)],
        device_id: int):
    device = device_crud_interface.get_one(db, Device.id == device_id)

    if not device:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No such device.")

    if device.owner_id != current_user.id:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User lacks permissions to acces this device.")

    topic = f"device/{device.id}/dispense"
    payload = "trigger"
    try:
        publish_single(topic, payload)
        return {"message": "Dispense command sent!"}
    except Exception:
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error")

