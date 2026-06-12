from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_AGILE_RATE_ENTITY,
    CONF_CHARGE_TOTAL_ENTITY,
    CONF_DISCHARGE_TOTAL_ENTITY,
    CONF_SYSTEM_COST,
    CONF_STARTING_SAVING,
    DEFAULT_SYSTEM_COST,
    DEFAULT_STARTING_SAVING,
)

class BatterySavingsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            await self.async_set_unique_id("battery_savings")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title="Battery Savings", data=user_input)

        schema = vol.Schema({
            vol.Required(
                CONF_AGILE_RATE_ENTITY,
                default="sensor.octopus_energy_electricity_20l3495049_2300001024206_current_rate",
            ): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
            vol.Required(
                CONF_CHARGE_TOTAL_ENTITY,
                default="sensor.givtcp_sd2525r010_energy_givtcp_battery_charge_energy_total_kwh",
            ): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
            vol.Required(
                CONF_DISCHARGE_TOTAL_ENTITY,
                default="sensor.givtcp_sd2525r010_energy_givtcp_battery_discharge_energy_total_kwh",
            ): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
            vol.Required(CONF_SYSTEM_COST, default=DEFAULT_SYSTEM_COST): selector.NumberSelector(
                selector.NumberSelectorConfig(min=0, max=20000, step=10, unit_of_measurement="£")
            ),
            vol.Required(CONF_STARTING_SAVING, default=DEFAULT_STARTING_SAVING): selector.NumberSelector(
                selector.NumberSelectorConfig(min=-20000, max=20000, step=1, unit_of_measurement="£")
            ),
        })

        return self.async_show_form(step_id="user", data_schema=schema)
