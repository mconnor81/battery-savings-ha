from __future__ import annotations

from datetime import timedelta

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.typing import StateType

from .const import (
    DOMAIN,
    CONF_AGILE_RATE_ENTITY,
    CONF_CHARGE_TOTAL_ENTITY,
    CONF_DISCHARGE_TOTAL_ENTITY,
    CONF_SYSTEM_COST,
    CONF_STARTING_SAVING,
)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    runtime = BatterySavingsRuntime(hass, entry)

    entities = [
        AgileRateGBP(runtime),
        BatteryChargeDelta(runtime),
        BatteryDischargeDelta(runtime),
        BatteryDischargeValueTotal(runtime),
        BatteryChargeCostTotal(runtime),
        BatteryNetSavingLifetime(runtime),
        BatteryPaybackRemaining(runtime),
    ]

    async_add_entities(entities)

    async def _tick(now):
        runtime.update_totals()
        for entity in entities:
            entity.async_write_ha_state()

    entry.async_on_unload(async_track_time_interval(hass, _tick, timedelta(minutes=1)))

class BatterySavingsRuntime:
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self.hass = hass
        self.entry = entry
        self.discharge_value_total = 0.0
        self.charge_cost_total = 0.0
        self.last_charge_kwh = None
        self.last_discharge_kwh = None
        self.last_charge_delta = 0.0
        self.last_discharge_delta = 0.0

    def state_float(self, entity_id: str, default=0.0) -> float:
        state = self.hass.states.get(entity_id)
        if state is None:
            return default
        try:
            return float(state.state)
        except (ValueError, TypeError):
            return default

    @property
    def agile_rate_gbp(self) -> float:
        raw = self.state_float(self.entry.data[CONF_AGILE_RATE_ENTITY])
        return raw / 100 if raw > 1 else raw

    @property
    def charge_total_kwh(self) -> float:
        return self.state_float(self.entry.data[CONF_CHARGE_TOTAL_ENTITY])

    @property
    def discharge_total_kwh(self) -> float:
        return self.state_float(self.entry.data[CONF_DISCHARGE_TOTAL_ENTITY])

    @property
    def system_cost(self) -> float:
        return float(self.entry.data.get(CONF_SYSTEM_COST, 0))

    @property
    def starting_saving(self) -> float:
        return float(self.entry.data.get(CONF_STARTING_SAVING, 0))

    def update_totals(self) -> None:
        charge_now = self.charge_total_kwh
        discharge_now = self.discharge_total_kwh

        if self.last_charge_kwh is None:
            self.last_charge_kwh = charge_now
            self.last_discharge_kwh = discharge_now
            return

        charge_delta = charge_now - self.last_charge_kwh
        discharge_delta = discharge_now - self.last_discharge_kwh

        self.last_charge_kwh = charge_now
        self.last_discharge_kwh = discharge_now

        if charge_delta < 0 or charge_delta > 10:
            charge_delta = 0
        if discharge_delta < 0 or discharge_delta > 10:
            discharge_delta = 0

        self.last_charge_delta = charge_delta
        self.last_discharge_delta = discharge_delta

        rate = self.agile_rate_gbp
        self.charge_cost_total += charge_delta * rate
        self.discharge_value_total += discharge_delta * rate

class BatterySavingsBase(SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, runtime: BatterySavingsRuntime):
        self.runtime = runtime
        self._attr_device_info = {
            "identifiers": {(DOMAIN, "battery_savings")},
            "name": "Battery Savings",
            "manufacturer": "Custom",
        }

class AgileRateGBP(BatterySavingsBase):
    _attr_name = "Agile Import Rate GBP"
    _attr_unique_id = "battery_savings_agile_import_rate_gbp"
    _attr_native_unit_of_measurement = "£/kWh"
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> StateType:
        return round(self.runtime.agile_rate_gbp, 5)

class BatteryChargeDelta(BatterySavingsBase):
    _attr_name = "Battery Charge Delta"
    _attr_unique_id = "battery_savings_charge_delta"
    _attr_native_unit_of_measurement = "kWh"
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> StateType:
        return round(self.runtime.last_charge_delta, 4)

class BatteryDischargeDelta(BatterySavingsBase):
    _attr_name = "Battery Discharge Delta"
    _attr_unique_id = "battery_savings_discharge_delta"
    _attr_native_unit_of_measurement = "kWh"
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> StateType:
        return round(self.runtime.last_discharge_delta, 4)

class BatteryDischargeValueTotal(BatterySavingsBase, RestoreEntity):
    _attr_name = "Battery Discharge Value Total"
    _attr_unique_id = "battery_savings_discharge_value_total"
    _attr_native_unit_of_measurement = "£"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    async def async_added_to_hass(self):
        if state := await self.async_get_last_state():
            try:
                self.runtime.discharge_value_total = float(state.state)
            except (ValueError, TypeError):
                pass

    @property
    def native_value(self) -> StateType:
        return round(self.runtime.discharge_value_total, 2)

class BatteryChargeCostTotal(BatterySavingsBase, RestoreEntity):
    _attr_name = "Battery Charge Cost Total"
    _attr_unique_id = "battery_savings_charge_cost_total"
    _attr_native_unit_of_measurement = "£"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.TOTAL

    async def async_added_to_hass(self):
        if state := await self.async_get_last_state():
            try:
                self.runtime.charge_cost_total = float(state.state)
            except (ValueError, TypeError):
                pass

    @property
    def native_value(self) -> StateType:
        return round(self.runtime.charge_cost_total, 2)

class BatteryNetSavingLifetime(BatterySavingsBase):
    _attr_name = "Battery Net Saving Lifetime"
    _attr_unique_id = "battery_savings_net_saving_lifetime"
    _attr_native_unit_of_measurement = "£"
    _attr_device_class = SensorDeviceClass.MONETARY

    @property
    def native_value(self) -> StateType:
        return round(self.runtime.starting_saving + self.runtime.discharge_value_total - self.runtime.charge_cost_total, 2)

class BatteryPaybackRemaining(BatterySavingsBase):
    _attr_name = "Battery Payback Remaining"
    _attr_unique_id = "battery_savings_payback_remaining"
    _attr_native_unit_of_measurement = "£"
    _attr_device_class = SensorDeviceClass.MONETARY

    @property
    def native_value(self) -> StateType:
        saved = self.runtime.starting_saving + self.runtime.discharge_value_total - self.runtime.charge_cost_total
        return round(max(self.runtime.system_cost - saved, 0), 2)
