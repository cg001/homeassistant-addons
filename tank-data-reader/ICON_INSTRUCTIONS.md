# Add-on Icon Instructions

To add a gas station icon for your add-on that will be displayed in the Home Assistant add-on overview, follow these steps:

## Requirements

1. The icon must be named `icon.png`
2. It should be placed in the root of the add-on directory (same level as config.json)
3. It should be square, preferably 256x256 pixels
4. It should have a transparent background for best appearance

## How to Get a Gas Station Icon

### Option 1: Download a Free Icon

You can download a free gas station icon from one of these sources:

1. [Flaticon](https://www.flaticon.com/free-icon/gas-station_115813) - Many free gas station icons
2. [Icons8](https://icons8.com/icons/set/gas-station) - High-quality icons, some free
3. [Iconfinder](https://www.iconfinder.com/search/?q=gas%20station&price=free) - Filter for free icons

### Option 2: Use a Material Design Icon

You can convert the Material Design Icon you're already using for the panel icon:

1. Visit [Material Design Icons](https://materialdesignicons.com/)
2. Search for "gas-station"
3. Download the SVG
4. Convert it to PNG using an online converter or image editor
5. Resize to 256x256 pixels

## Adding the Icon to Your Add-on

1. Rename your downloaded icon to `icon.png`
2. Place it in: `/Users/christiangraf/Library/CloudStorage/Dropbox/AVIATION/fsv HA/Tankstelle/homeassistant-addons/tank-data/`
3. Commit and push the changes to GitHub:
   ```bash
   cd /Users/christiangraf/Library/CloudStorage/Dropbox/AVIATION/fsv\ HA/Tankstelle/homeassistant-addons
   git add tank-data/icon.png
   git commit -m "Add gas station icon for add-on"
   git push
   ```

After updating your repository, the icon will appear in the Home Assistant add-on overview when you refresh the add-on store.
