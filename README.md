# PoolSync ChlorSync Integration for Home Assistant

This custom component adds support for **PoolSync™ ChlorSync®** by **AutoPilot®** to Home Assistant.

> ✅ Cloud-only integration using the official AWS API  
> ❌ No LAN/local control

## Features

This integration retrieves and displays real-time ChlorSync device data, including:

- 🌡️ Water temperature (°C)
- 🧂 Salt level (ppm)
- ⚡ Chlorine output (%), **read/write**
- 🔋 Output voltage (mV)
- 🧠 Cell rail voltage (mV)

> You can change the chlorine output using a number entity in Home Assistant (slider or automation).

## Installation

### Recommended: via [HACS](https://hacs.xyz)

1. Go to **HACS > Integrations > 3-dots menu > Custom repositories**
2. Add this repo:  
   `https://github.com/CLARENNE-Q/poolsync_chlorsync`
3. Category: **Integration**
4. Install "PoolSync ChlorSync"
5. Restart Home Assistant
6. Go to **Settings > Devices & Services > Add Integration**, search for **PoolSync ChlorSync**, and follow the login prompt

### Manual installation

1. Clone or download this repository to:  
   `custom_components/poolsync_chlorsync/`
2. Restart Home Assistant
3. Add the integration from the **Integrations** menu

## Limitations

- This integration is **read-only**
- Only works via Cloud; no local IP access
- Currently only supports **ChlorSync** devices

## Attribution

Developed by [Quentin Clarenne](https://github.com/CLARENNE-Q)  
PoolSync™ and ChlorSync® are trademarks of **AutoPilot®**

---

Contributions welcome — feel free to open issues or pull requests!
