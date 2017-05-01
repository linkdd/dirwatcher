# -*- coding: utf-8 -*-

import subprocess
import threading
import time
import sys
import os

USE_INOTIFY = False

try:
    import pyinotify

    fd = pyinotify.INotifyWrapper.create().inotify_init()

    if fd >= 0:
        USE_INOTIFY = True
        os.close(fd)

except ImportError:
    pass

USE_WINDOWS = (sys.platform == "win32")


class DirectoryWatcher(object):
    FILE_MODIFIED = 1
    ENVVAR = 'DIRWATCHER_RUN'

    def __init__(self, directory, script, *args, **kwargs):
        super(DirectoryWatcher, self).__init__(*args, **kwargs)

        if not os.path.exists(directory):
            raise RuntimeError(
                'No such file or directory: {0}'.format(directory)
            )

        if not os.path.isdir(directory):
            raise RuntimeError(
                'Path is not a directory: {0}'.format(directory)
            )

        self.directory = os.path.abspath(directory)
        self.script = script

        self.mtimes = {}

    def gen_filenames(self):
        for dirname, _, filenames in os.walk(self.directory):
            for filename in filenames:
                path = os.path.join(dirname, filename)
                yield path

    def inotify_watcher(self):
        class EventHandler(pyinotify.ProcessEvent):
            modified_code = None

            def process_default(self, event):
                EventHandler.modified_code = DirectoryWatcher.FILE_MODIFIED

        wm = pyinotify.WatchManager()
        notifier = pyinotify.Notifier(wm, EventHandler())

        mask = (
            pyinotify.IN_MODIFY |
            pyinotify.IN_DELETE |
            pyinotify.IN_ATTRIB |
            pyinotify.IN_MOVED_FROM |
            pyinotify.IN_MOVED_TO |
            pyinotify.IN_CREATE |
            pyinotify.IN_DELETE_SELF |
            pyinotify.IN_MOVE_SELF
        )

        for path in self.gen_filenames():
            wm.add_watch(path, mask)

        notifier.check_events(timeout=None)
        notifier.read_events()
        notifier.process_events()
        notifier.stop()

        return EventHandler.modified_code

    def watcher(self):
        for path in self.gen_filenames():
            stat = os.stat(filename)
            mtime = stat.st_mtime

            if USE_WINDOWS:
                mtime -= stat.st_ctime

            if filename not in self.mtimes:
                self.mtimes[filename] = mtime

            elif mtime != self.mtimes[filename]:
                return DirectoryWatcher.FILE_MODIFIED

        return None

    def reloader_thread(self):
        while True:
            change = self.inotify_watcher() if USE_INOTIFY else self.watcher()

            if change == DirectoryWatcher.FILE_MODIFIED:
                sys.exit(3)

            time.sleep(1)

    def restart_with_reloader(self):
        while True:
            exe = [sys.executable]
            warnopts = ['-W{0}'.format(o) for o in sys.warnoptions]
            args = exe + warnopts + sys.argv
            new_env = os.environ.copy()
            new_env[DirectoryWatcher.ENVVAR] = 'true'

            retcode = subprocess.call(args, env=new_env)

            if exit_code != 3:
                return exit_code

    def reloader(self):
        if os.environ.get(DirectoryWatcher.ENVVAR) == 'true':
            th = threading.Thread(target=self.launch_script)
            th.start()

            try:
                self.reloader_thread()

            except KeyboardInterrupt:
                pass

        else:
            try:
                exit_code = self.restart_with_reloader()

                if exit_code < 0:
                    os.kill(os.getpid(), -exit_code)

                else:
                    sys.exit(exit_code)

            except KeyboardInterrupt:
                pass

    def launch_script(self):
        subprocess.call(self.script, shell=True)