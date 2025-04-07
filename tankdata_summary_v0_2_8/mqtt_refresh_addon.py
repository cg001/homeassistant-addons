# Add this code to your main.py file in the addon

# Add this import if not already present
import paho.mqtt.client as mqtt

# Add this function to your existing code
def on_message(client, userdata, msg):
    """Handle incoming MQTT messages."""
    try:
        if msg.topic == "tankdaten/refresh":
            print("✅ Refresh requested via MQTT")
            # Call your existing fetch function
            fetch_newest_files()
    except Exception as e:
        print(f"❌ Error handling MQTT message: {e}")

# Modify your MQTT client setup to include message handling
# Find where you set up the MQTT client and add these lines:
mqtt_client.on_message = on_message
mqtt_client.subscribe("tankdaten/refresh")
