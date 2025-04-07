from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session
from crud.base import CRUDBase
from models.device import Device
from models.user import User
from schema.device import DeviceCreate, DeviceUpdate


class CRUDDevice(CRUDBase[Device, DeviceCreate, DeviceUpdate]):
    def set_thingsboard_id(self, db: Session, device: Device, thingsboard_id: UUID):
        """

        """
        device.thingsboard_id = thingsboard_id
        db.add(device)
        db.commit()
        db.refresh(device)
        return device
        
    def get_by_id(self, db: Session, id: UUID) -> Device:
        return self.get_one(db, Device.id == id)

    def set_provisioned_at(self, db: Session, device: Device) -> Device:
        device.provisioned_at = datetime.now(timezone.utc)
        db.add(device)
        db.commit()
        db.refresh(device)
        return device

    def set_owner(self, db: Session, device: Device, owner: User) -> Device:
        device.owner_id = owner.id
        db.add(device)
        db.commit()
        db.refresh(device)
        return device

device_crud_interface = CRUDDevice(Device)

