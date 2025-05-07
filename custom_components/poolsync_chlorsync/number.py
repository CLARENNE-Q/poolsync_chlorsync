from homeassistant.components.number import NumberEntity
from homeassistant.const import PERCENTAGE
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

NUMBER_CHLOR_OUTPUT = "chlor_output"

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([ChlorOutputNumber(coordinator)], True)

class ChlorOutputNumber(CoordinatorEntity, NumberEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "PoolSync ChlorSync Chlor Output Setpoint"
        self._attr_unique_id = "poolsync_chlorsync_chlor_output_number"
        self._attr_icon = "mdi:percent"
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_native_min_value = 0
        self._attr_native_max_value = 100
        self._attr_native_step = 1
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.mac)},
            "name": "PoolSync ChlorSync",
            "manufacturer": "PoolSync",
            "model": "ChlorSync",
        }

    @property
    def native_value(self):
        return self.coordinator.data["devices"]["0"]["config"].get("chlorOutput")

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_set_chlor_output(int(value))
        await self.coordinator.async_request_refresh()
