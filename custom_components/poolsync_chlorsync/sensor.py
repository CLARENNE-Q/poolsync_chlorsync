from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.const import (
    UnitOfTemperature,
    UnitOfElectricPotential,
    PERCENTAGE,
    CONCENTRATION_PARTS_PER_MILLION,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

SENSORS = [
    ("water_temp", "Water Temp", SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS),
    ("salt_ppm", "Salt Ppm", None, CONCENTRATION_PARTS_PER_MILLION),
    ("chlor_output", "Chlor Output", None, PERCENTAGE),
    ("out_voltage", "Output Voltage", SensorDeviceClass.VOLTAGE, UnitOfElectricPotential.MILLIVOLT),
    ("cell_rail_voltage", "Cell Rail Voltage", SensorDeviceClass.VOLTAGE, UnitOfElectricPotential.MILLIVOLT),
]

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    sensors = [
        PoolSyncChlorSyncSensor(coordinator, sensor_type, name, device_class, unit)
        for sensor_type, name, device_class, unit in SENSORS
    ]
    async_add_entities(sensors, True)

class PoolSyncChlorSyncSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, sensor_type, name, device_class, unit):
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._sensor_type = sensor_type
        self._attr_name = f"PoolSync ChlorSync {name}"
        self._attr_unique_id = f"poolsync_chlorsync_{sensor_type}"
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = unit
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.mac)},
            "name": "PoolSync ChlorSync",
            "manufacturer": "PoolSync",
            "model": "ChlorSync",
            "sw_version": None,
        }

    @property
    def extra_state_attributes(self):
        try:
            mac = self.coordinator.data["poolSync"]["system"].get("macAddr")
            return {"mac_bssid": mac} if mac else {}
        except Exception:
            return {}

    @property
    def native_value(self):
        data = self.coordinator.data
        try:
            if self._sensor_type == "water_temp":
                temp_f = data["devices"]["0"]["status"].get("waterTemp")
                return round((temp_f - 32) * 5 / 9, 2) if temp_f is not None else None
            elif self._sensor_type == "salt_ppm":
                return data["devices"]["0"]["status"].get("saltPPM")
            elif self._sensor_type == "chlor_output":
                return data["devices"]["0"]["config"].get("chlorOutput")
            elif self._sensor_type == "out_voltage":
                return data["devices"]["0"]["status"].get("outVoltage")
            elif self._sensor_type == "cell_rail_voltage":
                return data["devices"]["0"]["status"].get("cellRailVoltage")
        except Exception as e:
            self._attr_available = False
            return None
