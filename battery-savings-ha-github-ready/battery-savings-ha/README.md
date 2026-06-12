# Battery Savings for Home Assistant

A custom Home Assistant integration for estimating battery savings on Octopus Agile using cumulative battery charge and discharge energy sensors.

## Installation with HACS

1. Open HACS
2. Go to **Integrations**
3. Click the three dots → **Custom repositories**
4. Add this repository URL
5. Category: **Integration**
6. Install **Battery Savings**
7. Restart Home Assistant
8. Go to **Settings → Devices & services → Add integration**
9. Search for **Battery Savings**

## Manual install

Copy:

```text
custom_components/battery_savings
```

to:

```text
/config/custom_components/battery_savings
```

Restart Home Assistant.

## Entities used

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

## Disclaimer

This is an estimate. The most accurate calculation would use exact half-hour price periods matched to recorded charge and discharge events.
