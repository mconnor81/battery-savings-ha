# Battery Savings for Home Assistant

A custom Home Assistant integration for estimating battery savings on Octopus Agile using cumulative battery charge and discharge energy sensors.

Built originally for a GivEnergy Gen 1 hybrid inverter with GivTCP and Octopus Agile.

## What it creates

- Agile import rate in £/kWh
- Battery charge delta
- Battery discharge delta
- Battery discharge value total
- Battery charge cost total
- Net lifetime saving
- Payback remaining

## Install with HACS

1. Open HACS
2. Go to **Integrations**
3. Click the three dots → **Custom repositories**
4. Add your GitHub repository URL
5. Category: **Integration**
6. Install **Battery Savings**
7. Restart Home Assistant
8. Go to **Settings → Devices & services → Add integration**
9. Search for **Battery Savings**

## Manual install

Copy this folder:

```text
custom_components/battery_savings
```

to:

```text
/config/custom_components/battery_savings
```

Restart Home Assistant.

## Suggested entities for Matthew's setup

Agile import rate:

```text
sensor.octopus_energy_electricity_20l3495049_2300001024206_current_rate
```

Battery charge total:

```text
sensor.givtcp_sd2525r010_energy_givtcp_battery_charge_energy_total_kwh
```

Battery discharge total:

```text
sensor.givtcp_sd2525r010_energy_givtcp_battery_discharge_energy_total_kwh
```

## How it works

The integration watches cumulative battery charge and discharge kWh totals. When these totals increase, it multiplies the energy delta by the current Agile import rate.

```text
Discharge value = discharge kWh delta × current Agile import price
Charge cost = charge kWh delta × current Agile import price
Net saving = starting saving + discharge value total - charge cost total
```

Negative Agile prices are handled correctly.

## Disclaimer

This is an estimate. The most accurate calculation would use exact half-hour price periods matched to recorded charge and discharge events. This integration is intended as a practical Home Assistant approximation.
