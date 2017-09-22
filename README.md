Python script for querying X-server information and manipulating X-windows

# Actions

## --move-\<id>-\<width>x\<height>+\<x>+\<y>

move an X window to the specified position

## --print-window-info

print information on X windows  
format: `<id> <geometry> <frame_extents> <window_workspace>:<current_workspace> <tags> <class> <title>`  
separated by tabs

## --print-active-window-info

print information on the active X window

## --print-active-window-id

print the id of the active X window

## --print-monitor-info

print information on active monitors  
format: `<name> <id> <geometry>`  
separated by tabs

## --version

show version


# Dependencies

-python-xlib (can be out of date in some distro repos - see [#2](https://github.com/xhsdf/pxdo/issues/2))
