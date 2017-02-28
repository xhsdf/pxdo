Python script for querying X-server information and moving X-windows

#Actions

##--get-window-info

print information on X windows  
format: <id> <geometry> <frame_extents> <window_workspace>:<current_workspace> <tags> <class> <title>  
separated by tabs

##--get-active-window-info

print information on the active X window

##--get-active-window-id

print the id of the active X window

##--get-monitor-info

print information on active monitors  
format: <name> <id> <geometry>  
separated by tabs

##--version

show version


#Dependencies

-python-xlib
