from datetime import datetime, timezone
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from src.crud.base import CRUDBase
from src.models.device import Device
from src.schemas.devices import DeviceCreate, DeviceUpdate


class CRUDDevice(CRUDBase[Device, DeviceCreate, DeviceUpdate]):
    def get_devices_with_owner(self, db: Session, owner_id: UUID) -> List[Device]:
        devices = self.get_many(db, self.model.owner_id == owner_id)
        return devices
    
    def set_is_provisioned(self, db: Session, device: Device) -> Device:
        device.provisioned_at = datetime.now(timezone.utc)
        db.add(device)
        db.commit()
        db.refresh(device)
        return device

device_crud_interface = CRUDDevice(Device)

