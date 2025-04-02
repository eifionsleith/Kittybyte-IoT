from crud.base import CRUDBase
from models.device import Device
from schema.device import DeviceCreate, DeviceUpdate


class DeviceCRUD(CRUDBase[Device, DeviceCreate, DeviceUpdate]):
    ...

device_crud_interface = DeviceCRUD(Device)
