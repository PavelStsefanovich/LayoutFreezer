# LayoutFreezer

LayoutFreezer is a system tray app that allows users to save coordinates for opened windows for each display configuration (that is number of displays, their sizes, orientation and location relative to each other). These coordinates can be used at a later time to restore desired window layout after any change, like moving/resizing opened applications or connection/disconnection to external monitors.

After starting LF for the first time, a user will need to position opened windows into desired layout and then 'Freeze Layout', which will save current display configuration and any opened windows configuration into the database. Users can add new apps window configurations into the database later by running 'Freeze Layout' again. Users can also save apps layout for each display configurations they work with (for example, you can have one external monitor at home and three-monitor docking station at work; or work in rotation with monitors in landscape and portrait orientation).

A user can then reposition/resize windows for opened applications in one click to match saved coordinates for each opened app for current display configuration. Matching applications are determined by process name and title. If title does not match exactly, the config with most similar title will be selected. If no similar titles are found, LF will attempt to guess the most suitable position configuration considering all saved configs for current app. Nothing will happen for opened windows that don't have at least a single configuration saved into the database.

***This project is currently being developed, so not all of the announced functionality is implemented yet*** 


---
### Roadmap:
- Guess best location for an opened app that has config(s) saved for current display layout with non-matching title(s)
- Guess best location for an opened app that has config saved for other display layout(s), but not for current one.
- Preferences edit dialog
- Key shortcuts
- Install/Uninstall scripts