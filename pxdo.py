#!/usr/bin/python


NAME = "pxdo"
VERSION = "0.10"


import sys, re
import Xlib.display
import Xlib.X as X
import Xlib.Xatom as Xatom
import Xlib.protocol as protocol
import Xlib.ext.randr as randr

display = None
MOVE_REGEX = '--move-(0x[0-9a-fA-F]+)-(\\d+)x(\\d+)\\+(\\d+)\\+(\\d+)'

def main(argv):
	globals()['display'] = Xlib.display.Display()

	for arg in argv:
		try:
			if arg == '--version':
				print("%s v%s" % (NAME, VERSION))
			elif arg == '--get-active-window-id':
				print("0x%x" % Window.get_active_window_id())
			elif arg == '--get-active-window-info':
				print_active_window_info()
			elif arg == '--get-window-info':
				print_window_info()
			elif arg == '--get-monitor-info':
				print_monitor_info()
			elif re.match(MOVE_REGEX, arg):
				p = re.compile(MOVE_REGEX)
				wid, width, height, x, y = p.findall(arg)[0]
				w = Window.from_id(int(wid, 16), False)
				w.move(int(x), int(y), int(width), int(height))
		except:
			print("Unexpected error:", sys.exc_info()[0])

	display.sync()
	display.flush()
	display.close()


def print_window_info():
	window_ids = Window.get_window_ids()
	for w in Window.get_windows():
		print("WINDOW: " + w.get_info_string())


def print_monitor_info():
	for monitor in Monitor.get_monitors():
		print("MONITOR: " + monitor.get_info_string())


def print_active_window_info():
	w = Window.from_id(int(Window.get_active_window_id()))
	w.active = True
	print(w.get_info_string())

class Monitor:
	def __init__(self, mon_id, x, y, width, height):
		self.id = mon_id
		self.x, self.y, self.width, self.height = x, y, width, height
		self.name = ""


	# <name>	<id>	<geometry>
	def get_info_string(self):
		return "%s\t%d\t%dx%d+%d+%d" % (self.name, self.id, self.width, self.height, self.x, self.y)


	@staticmethod
	def get_monitors():
		resources = randr.get_screen_resources(display.screen().root)
		monitors = {}
		for crtc in resources.crtcs:
			crtc_info = display.xrandr_get_crtc_info(crtc, resources.config_timestamp)
			for output_id in crtc_info.outputs:
				monitor = Monitor(output_id, crtc_info.x, crtc_info.y, crtc_info.width, crtc_info.height)
				monitors[output_id] = monitor


		output_ids = randr.get_screen_resources(display.screen().root).outputs
		for monitor in monitors.values():
			output_info = randr.get_output_info(display.screen().root, monitor.id, 0)
			monitor.name = output_info.name

		#~ for monitor in monitors.values():
			#~ print("MONITOR: " + monitor.get_info_string())
		return monitors.values()


class Window:
	def __init__(self, win, win_id, full = True):
		self.win = win
		self.win_id = win_id
		self.active = False
		self.name = self.wm_class = "Unknown"
		self.workspace = -1
		self.hidden = False
		self.fullscreen = False
		self.allowed_actions = []
		self.x, self.y, self.width, self.height = 0, 0, 0, 0
		self.extents_left, self.extents_right, self.extents_top, self.extents_bottom = 0, 0, 0, 0
		extents = self.get_property('_NET_FRAME_EXTENTS')
		if extents != None:
			self.extents_left, self.extents_right, self.extents_top, self.extents_bottom = extents
		if full:
			self.name = self.get_property('WM_NAME').decode("ascii", errors='ignore').replace("\t", "  ")
			self.workspace = int(self.get_property('_NET_WM_DESKTOP')[0])
			self.allowed_actions = self.get_property('_NET_WM_ALLOWED_ACTIONS')
			self.state = self.get_property('_NET_WM_STATE')
			if display.intern_atom("_NET_WM_STATE_HIDDEN") in self.state:
				self.hidden = True
			if display.intern_atom("_NET_WM_STATE_FULLSCREEN") in self.state:
				self.fullscreen = True
			self.wm_class = win.get_wm_class()[1]
			geometry = win.query_tree().parent.get_geometry()
			self.x = geometry.x
			self.y = geometry.y
			self.width = geometry.width
			self.height = geometry.height


	@staticmethod
	def get_windows():
		windows = []
		active_window_id = Window.get_active_window_id()
		for win_id in Window.get_window_ids():
			w = Window.from_id(int(win_id))
			if win_id == active_window_id:
				w.active = True
			if display.intern_atom("_NET_WM_ACTION_MOVE") in w.allowed_actions or display.intern_atom("_NET_WM_ACTION_RESIZE") in w.allowed_actions:
				windows.append(w)
		return windows


	@staticmethod
	def from_id(wid, full = True):
		return Window(display.create_resource_object('window', wid), wid, full)


	# <id>	<geometry>	<frame_extents>	<window_workspace>:<current_workspace>	<tags>	<class>	<title>
	def get_info_string(self):
		tags = ","
		if self.hidden:
			tags += "hidden,"
		if self.fullscreen:
			tags += "fullscreen,"
		if self.active:
			tags += "active,"
		current_workspace = Window.get_current_workspace();
		return "0x%x\t%s\t%s\t%d:%d\t%s\t%s\t%s" % (self.win_id, "%dx%d+%d+%d" % (self.width, self.height, self.x, self.y), "%d,%d,%d,%d" % (self.extents_top, self.extents_bottom, self.extents_left, self.extents_right), self.workspace, current_workspace, tags, self.wm_class, self.name)


	def move(self, x, y, width, height):
		window = self.win

		width -= self.extents_left + self.extents_right
		height -= self.extents_top + self.extents_bottom

		gravity=0
		gravity_flags = gravity | 0b0000000010000000 # ???
		gravity_flags = gravity_flags | 0b0000000100000000 # x
		gravity_flags = gravity_flags | 0b0000001000000000 # y
		gravity_flags = gravity_flags | 0b0000010000000000 # w
		gravity_flags = gravity_flags | 0b0000100000000000 # h
		wm_normal_hints = window.get_wm_normal_hints()
		if wm_normal_hints != None:
			wm_normal_hints["width_inc"] = 0
			wm_normal_hints["height_inc"] = 0
			window.set_wm_normal_hints(wm_normal_hints)
		self.set_property('_NET_MOVERESIZE_WINDOW', [gravity_flags, int(x), int(y), int(width), int(height)])


	def get_property(self, prop):
		atom = self.win.get_full_property(display.intern_atom(prop), X.AnyPropertyType)
		if atom:
			return atom.value
		else:
			return None


	def set_property(self, prop, data, mask=None):
		if isinstance(data, str):
			datasize = 8
		else:
			data = (data+[0]*(5-len(data)))[:5]
			datasize = 32

		event = protocol.event.ClientMessage(window=self.win, client_type=display.intern_atom(prop), data=(datasize, data))

		if not mask:
			mask = (X.SubstructureRedirectMask|X.SubstructureNotifyMask)
		display.screen().root.send_event(event, event_mask=mask)


	@staticmethod
	def get_current_workspace():
		return Window(display.screen().root, 0, False).get_property('_NET_CURRENT_DESKTOP')[0]


	@staticmethod
	def get_active_window_id():
		return Window(display.screen().root, 0, False).get_property('_NET_ACTIVE_WINDOW')[0]


	@staticmethod
	def get_window_ids():
		return Window(display.screen().root, 0, False).get_property('_NET_CLIENT_LIST_STACKING')


if __name__ == "__main__":
	main(sys.argv[1:])
