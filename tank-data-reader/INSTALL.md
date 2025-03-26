# Installation Guide for Tank Data Reader Add-on

This guide will help you install the Tank Data Reader add-on in your Home Assistant instance.

## Prerequisites

- A running Home Assistant instance (Core, OS, or Container)
- Access to the Home Assistant Add-on Store
- SFTP server with tank data XML files
- MQTT broker (the Mosquitto broker add-on is recommended)

## Installation Steps

### 1. Add the Repository to Home Assistant

1. In Home Assistant, navigate to **Settings** → **Add-ons** → **Add-on Store**
2. Click the menu (⋮) in the top right corner and select **Repositories**
3. Add the repository URL: `https://github.com/cg001/homeassistant-addons`
4. Click **Add**

### 2. Install the Add-on

1. The Tank Data Reader add-on should now appear in the add-on store
2. Click on it and then click **Install**
3. Wait for the installation to complete

### 3. Configure the Add-on

1. After installation, go to the **Configuration** tab
2. Configure the following settings:
   - `sftp_host`: The hostname or IP address of your SFTP server
   - `sftp_port`: The port of your SFTP server (usually 22)
   - `sftp_username`: Your SFTP username
   - `sftp_password`: Your SFTP password
   - `sftp_path`: The path on the SFTP server where the XML files are located
   - `mqtt_host`: The hostname or IP address of your MQTT broker (use `core-mosquitto` for the Mosquitto add-on)
   - `mqtt_port`: The port of your MQTT broker (usually 1883)
   - `mqtt_username`: Your MQTT username (if required)
   - `mqtt_password`: Your MQTT password (if required)
   - `mqtt_topic_prefix`: The prefix for MQTT topics (default: `tank_data`)
   - `update_interval`: How often to check for new files (in seconds)
   - `log_level`: The log level for the add-on
3. Click **Save** to save your configuration

### 4. Start the Add-on

1. Go to the **Info** tab
2. Click **Start**
3. Check the logs to make sure everything is working correctly

### 5. Access the Web Interface

1. The web interface is available at the URL shown in the add-on info page
2. You can also access it from the Home Assistant sidebar if you've enabled the Show in sidebar option

### 6. Add to Home Assistant Dashboard

To add the tank data to your Home Assistant dashboard:

1. Go to your dashboard and click **Edit Dashboard**
2. Click the **+ Add Card** button
3. Choose **Entities** or **Markdown** card type
4. Add the MQTT sensors that the add-on creates:
   - `sensor.tank_data_last_update`
   - `sensor.tank_data_total_quantity`
   - etc.
5. Save your dashboard

## Troubleshooting

If you encounter any issues:

1. Check the add-on logs for error messages
2. Verify your SFTP and MQTT configuration
3. Make sure your SFTP server is accessible from Home Assistant
4. Check that the XML files are in the expected format

## Updating

When updates are available:

1. Go to the add-on page in Home Assistant
2. Click **Update**
3. The add-on will be updated to the latest version

## Uninstalling

If you need to uninstall the add-on:

1. Stop the add-on
2. Click **Uninstall**
3. Remove the repository if you no longer need it
