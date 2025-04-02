from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.dependencies.auth import get_current_superuser, get_user_from_jwt
from api.dependencies.database import get_db
from models.device import Device
from models.user import User
from schema.device import DeviceCreate, DeviceOutput, DeviceUpdate
from crud.device import device_crud_interface


router = APIRouter()

@router.post("/create", response_model=DeviceOutput)
def create_device(
        db: Annotated[Session, Depends(get_db)],
        current_superuser: Annotated[User, Depends(get_current_superuser)]) -> DeviceOutput:
    """
    Creates a new device in the system, only avaiable to superusers.
    """
    device_create = DeviceCreate(creator_id=current_superuser.id)
    device = device_crud_interface.create(db, device_create)
    return device

@router.delete("/delete", response_model=bool)
def delete_device(
        db: Annotated[Session, Depends(get_db)],
        current_superuser: Annotated[User, Depends(get_current_superuser)],
        device_id: UUID) -> bool:
    """
    Deletes a device, by it's UUID, from the system. Only avaiable to superusers.
    """
    return device_crud_interface.delete(db, Device.id == device_id)

@router.post("/{device_id}/register", response_model=DeviceOutput)
def register_device_to_user(
        device_id: UUID,
        db: Annotated[Session, Depends(get_db)],
        current_user: Annotated[User, Depends(get_user_from_jwt)]) -> DeviceOutput:
    """
    Registers the device with provided ID to the current user, 
    assuming both are valid.
    """
    device = device_crud_interface.get_one(db, Device.id == device_id)
    if device is None:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No such device with ID: {device_id}")
    
    if device.owner is None:
        device_update = DeviceUpdate(owner_id=current_user.id)
        device = device_crud_interface.update(db, device, device_update)
        return device
    else:
        raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Device already has an owner.")

@router.post("/{device_id}/unregister")
def unregister_device_from_current_user(
        device_id: UUID,
        db: Annotated[Session, Depends(get_db)],
        current_user: Annotated[User, Depends(get_user_from_jwt)]) -> bool:
    """
    Removes the currently authenticated user as the owner for 
    the given device, assuming they are currently the owner.
    """
    device = device_crud_interface.get_one(db, Device.id == device_id)
    if device is None:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device with ID '{device_id}' not found.")
    
    if device.owner_id != current_user.id:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current user does not have permission to do this.")

    device = device_crud_interface.update(db, device, DeviceUpdate(owner_id=None))
    return True

@router.post("/{device_id}/dispense")
def dispense(
        db: Annotated[Session, Depends(get_db)],
        current_user: Annotated[User, Depends(get_user_from_jwt)],
        dispense_amount: int,
        device_id: int):
    """
    Sends a message to the device to dispense the provided amount 
    of food, in grams.
    """
    device = device_crud_interface.get_one(db, Device.id == device_id)
    if not device:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device with ID '{device_id}' not found.")

    if device.owner_id != current_user.id:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current user does not have permission to do this.")

    topic = f"device/{device.id}/dispense"
    payload = f"qty:{dispense_amount}"
    #! TODO: MQTT Message Handling

