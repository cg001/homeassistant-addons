# Tankdaten Dashboard Configuration

This directory contains configuration files for displaying the Tankdaten MQTT data in a Home Assistant dashboard.

## Installation Instructions

### Step 1: Add the MQTT Sensor

Add the contents of `mqtt_sensor.yaml` to your Home Assistant configuration. You can either:

- Copy the contents directly into your `configuration.yaml` file, or
- Use the `!include` directive to include the file:

```yaml
# In configuration.yaml
mqtt: !include mqtt_sensor.yaml
```

### Step 2: Restart Home Assistant

After adding the MQTT sensor configuration, restart Home Assistant to apply the changes.

### Step 3: Add the Lovelace Card

Choose one of the four provided Lovelace card options:

- **Option A (`lovelace_card_option_a.yaml`)**: Uses a custom table card (requires HACS with `lovelace-table-card` installed)
- **Option B (`lovelace_card_option_b.yaml`)**: Uses the built-in entities card (simpler but less table-like)
- **Option C (`lovelace_card_option_c.yaml`)**: Uses a markdown card to create a table (good balance of simplicity and appearance)
- **Option D (`lovelace_card_option_d.yaml`)**: Uses card-mod for advanced styling (requires HACS with `card-mod` installed)

To add the card to your dashboard:

1. Go to your Home Assistant dashboard
2. Click the three dots in the top-right corner and select "Edit Dashboard"
3. Click the "+" button to add a new card
4. Select "Manual" at the bottom
5. Copy and paste the contents of your chosen option
6. Click "Save"

## How It Works

- The MQTT sensor subscribes to the "tankdaten" topic where your addon publishes data
- The sensor stores the transaction data as attributes
- The Lovelace card displays this data in a table format
- The refresh button publishes a message to the "tankdaten/refresh" topic, which triggers a new data fetch in the addon

## Addon Modifications Required

To enable the refresh button functionality, you need to add the code from `mqtt_refresh_addon.py` to your addon's `main.py` file. This code:

1. Sets up a message handler for the MQTT client
2. Subscribes to the "tankdaten/refresh" topic
3. Triggers the `fetch_newest_files()` function when a refresh message is received

After making these changes, restart your addon for the changes to take effect.

## Troubleshooting

If you don't see any data:

1. Check that your addon is publishing to the "tankdaten" MQTT topic
2. Verify that the MQTT integration in Home Assistant is properly configured
3. Check Home Assistant logs for any errors related to the MQTT sensor
4. Try manually refreshing the entity using Developer Tools > Services > `homeassistant.update_entity`
