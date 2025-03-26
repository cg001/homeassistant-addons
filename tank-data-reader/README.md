# Tank Data Reader Add-on for Home Assistant

This add-on reads tank transaction data from an SFTP server, processes it, and makes it available in Home Assistant through MQTT and a web interface.

## Features

- Connects to SFTP server to download tank transaction data
- Processes XML files to extract transaction information
- Publishes data to MQTT for use in Home Assistant automations and dashboards
- Provides a web interface to view transaction data
- Includes a refresh button to fetch the latest data on demand

## Installation

1. Add this repository to your Home Assistant instance
2. Install the "Tank Data Reader" add-on
3. Configure the add-on (see Configuration section)
4. Start the add-on

## Configuration

### Add-on Configuration

```yaml
sftp_host: 192.168.5.205
sftp_port: 22
sftp_username: tankdaten
sftp_password: fsv2000
sftp_path: /DiskC/Datatransfers/Upload/Data
mqtt_host: core-mosquitto
mqtt_port: 1883
mqtt_username: ""
mqtt_password: ""
mqtt_topic_prefix: tank_data
update_interval: 300
log_level: info
```

### Option: `sftp_host`

The hostname or IP address of the SFTP server.

### Option: `sftp_port`

The port of the SFTP server (usually 22).

### Option: `sftp_username`

The username to use for SFTP authentication.

### Option: `sftp_password`

The password to use for SFTP authentication.

### Option: `sftp_path`

The path on the SFTP server where the XML files are located.

### Option: `mqtt_host`

The hostname or IP address of the MQTT broker. Use `core-mosquitto` to use the Mosquitto broker add-on.

### Option: `mqtt_port`

The port of the MQTT broker (usually 1883).

### Option: `mqtt_username`

The username to use for MQTT authentication. Leave empty if no authentication is required.

### Option: `mqtt_password`

The password to use for MQTT authentication. Leave empty if no authentication is required.

### Option: `mqtt_topic_prefix`

The prefix to use for MQTT topics. All topics will be prefixed with this value.

### Option: `update_interval`

The interval in seconds between updates. The add-on will check for new files on the SFTP server at this interval.

### Option: `log_level`

The log level for the add-on. Possible values are `trace`, `debug`, `info`, `warning`, `error`, and `fatal`.

## MQTT Topics

The add-on publishes data to the following MQTT topics:

- `{mqtt_topic_prefix}/last_update`: The timestamp of the last update
- `{mqtt_topic_prefix}/transactions`: A JSON array of all transactions
- `{mqtt_topic_prefix}/transaction/{id}`: Individual transaction data
- `{mqtt_topic_prefix}/status`: The status of the add-on (online/offline)

## Web Interface

The add-on provides a web interface that can be accessed from the Home Assistant sidebar. The interface shows a table of all transactions and includes a refresh button to fetch the latest data on demand.

## Troubleshooting

### Logs

The add-on logs can be viewed in the Home Assistant UI under Settings → System → Logs, or on the add-on's info page under the Logs tab.

### Common Issues

- **Connection refused**: Check that the SFTP server is running and accessible from Home Assistant
- **Authentication failed**: Check the SFTP username and password
- **No files found**: Check the SFTP path and ensure there are XML files in that location
- **MQTT connection failed**: Check the MQTT broker settings

## Support

If you have any issues or questions, please open an issue on the GitHub repository.

## License

This add-on is licensed under the MIT License.
