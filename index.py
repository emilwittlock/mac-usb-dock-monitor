import re
import subprocess
import rumps
import configparser


class DockMonitorApp(object):
    def __init__(self):

        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

        self.dock_state = None
        self.app = rumps.App("DockMonitor", )
        self.app = rumps.App("Dock Monitor")
        self.timer = rumps.Timer(
            self.on_tick, self.config.getint("DEFAULT", "poll_interval"))

        # Menu creation
        self.set_up_menu()
        self.start_button = rumps.MenuItem(
            title="Start monitor", callback=self.start_monitor)
        self.stop_button = rumps.MenuItem(
            title="Stop monitor", callback=None)
        self.settings_button = rumps.MenuItem(
            title="Settings", callback=self.settings)
        self.app.menu = [self.start_button, self.stop_button,
                         None, self.settings_button, None]

    def set_up_menu(self):
        self.timer.stop()
        self.timer.count = 0
        self.app.title = "🦆✋"

    # Main monitoring loop

    def on_tick(self, sender):
        devices = self.fetch_devices()
        devices = self.match_usbdock(devices)

        if len(devices) >= 1:
            current_state = True
            self.app.title = "🦆👍"
        else:
            current_state = False
            self.app.title = "🦆👎"

        if current_state != self.dock_state:
            # Bluetooth should be toggled
            if self.toggle_bluetooth(current_state) == True:
                self.dock_state = current_state

    # Start button callback

    def start_monitor(self, sender):
        self.timer.start()
        self.start_button.set_callback(None)
        self.stop_button.set_callback(self.stop_monitor)

    # Stop button callback
    def stop_monitor(self, sender):
        self.timer.stop()
        self.start_button.set_callback(self.start_monitor)
        self.stop_button.set_callback(None)
        self.app.title = "🦆✋"
        # Settings button callback

    def settings(self, sender):
        settings = rumps.Window(
            message='USB device search pattern', title='Settings', default_text=self.config["DEFAULT"]["devices"], ok=None, cancel=None, dimensions=(320, 160))

        response = settings.run()
        self.config["DEFAULT"]["devices"] = response.text
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)

    # Search for connected USB devices
    def fetch_devices(self):
        try:
            device_re = re.compile(
                b"Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
            df = subprocess.check_output(self.config["DEFAULT"]["lsusb"])
            devices = []
            for i in df.split(b'\n'):
                if i:
                    info = device_re.match(i)
                    if info:
                        dinfo = info.groupdict()
                        devices.append(dinfo["id"].decode("utf-8"))
            return devices
        except:
            rumps.notification(title=self.config["app_name"], subtitle='Error',
                               message='Failed to search for USB devices.\n\'lsusb\' installed?')
            self.stop_monitor()

    # Search for connected USB docks
    def match_usbdock(self, devices):
        r = re.compile(self.config["DEFAULT"]["devices"])
        matches = list(filter(r.match, devices))
        return matches

    # Toggle Bluetooth

    def toggle_bluetooth(self, state):
        cmd = [self.config["DEFAULT"]["blueutil"],  "-p", str(int(state))]
        try:
            output = subprocess.check_output(cmd)
            if output == b"":
                return True
        except:
            rumps.notification(title="Dock Monitor", subtitle='Error',
                               message='Failed to toggle Bluetooth.\n\'blueutil\' installed?')
            self.stop_monitor()
        return False

    def run(self):
        self.app.run()


if __name__ == '__main__':
    app = DockMonitorApp()
    app.run()
