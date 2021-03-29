# LayoutFreezer
[logo](icons/layoutfreezer.png)

LayoutFreezer is a system tray app that allows users to save coordinates for opened windows for each display configuration (that is number of displays, their sizes, orientation and location relative to each other). These coordinates can be used at a later time to restore desired window layout after any change, like moving/resizing opened applications or connecting/disconnecting external monitors.

### Current Release: 0.4.3
#### Release Notes:
- Added support for hotkeys
- Added icons and hotkey indicators to menu items
- Implemented GUI dialogs: About, Preferences, Warning
- Split Clear Database into two options: Current Layout and Everything
- Implemented old logs disposal (max number of log files is set in config.yml)
- Added Install/Uninstall scripts (Windows)

## How To:
After starting LF for the first time, a user will need to position opened windows into desired layout and run 'Freeze Layout' command, which will save current display configuration and any opened windows configurations into the database. Users can add new apps window configurations into the database later by running 'Freeze Layout' again. Users can also save apps layouts for each display configurations they work with (for example, you can have one external monitor at home and three-monitor docking station at work; or work in rotation with monitors in landscape and portrait orientation).

A user can then reposition/resize windows for opened applications in one click to match saved coordinates for each opened app for current display configuration. Matching applications are determined by process name and title. If title does not match exactly, the config with most similar title will be selected. If no similar titles are found, LF will attempt to guess the most suitable position configuration considering all saved configs for current app. Nothing will happen for opened windows that don't have at least a single configuration saved into the database.

## Roadmap:
- Guess best location for an opened app that has config(s) saved for current display layout with non-matching title(s)
- Guess best location for an opened app that has config saved for other display layout(s), but not for current one.
- Auto-Upgrade pref file on version change; warn user if preferences are reset to defaults
###### Tentative:
- ? Preferences validation in case user edited it manually
- ? Implement handling of windows for app running with elevated privileges (currently unable to enumerate: access denied)
- ? Add known invisible system apps to exclude list

###### Dropped:
- Cosmetic: in Preferences dialog make parameters names bold (groupbox title)
