"""Defines a context manager class `ChromeProcess` that takes care of
starting/stopping a Chrome/Chromium process in headless mode.
"""
from typing import Optional, List, Tuple, IO

import os
import subprocess  # nosec: B404
import tempfile
import signal
import time
import logging


from PythonChromiumHTML2PDF.chrome_api import ChromeApi


logger = logging.getLogger(__name__)


def _get_path_for_command(command: str) -> Optional[str]:
    try:
        return (subprocess.check_output(['which', command],  # nosec: # B607
                                        shell=False)
                .decode('utf-8')
                .replace('\n', ''))
    except Exception:
        return None


class ChromeProcess:

    DEFAULT_PORT = 9222
    DEFAULT_TIMEOUT = 10  # seconds
    HEADLESS_FLAGS = [
        '--headless',
        '--disable-gpu',
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--single-process',
        '--no-zygote',
    ]
    FONT_FLAGS = [
        '--font-render-hinting=none',
        '--enable-font-antialiasing',
    ]

    def __init__(self,
                 binary_path: Optional[str] = None,
                 port: Optional[int] = None,
                 timeout: Optional[float] = None,
                 flags: Optional[List[str]] = None):

        if binary_path is None:
            binary_path = self.find_installed_chrome_path()

        return_values = self.start_chrome(binary_path, port, flags)
        self.chrome_process: subprocess.Popen = return_values[0]
        self.log_file: IO = return_values[1]
        self.log_path: str = return_values[2]
        self.pid: int = self.chrome_process.pid
        self.api: ChromeApi = self.connect_to_chrome(port, timeout)
        self.terminated = False

    def __del__(self):
        try:
            if not self.terminated:
                self.terminate()
        except AttributeError:
            pass  # nosec: B110

    def __enter__(self) -> ChromeApi:
        return self.api

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.terminate()

    @staticmethod
    def find_installed_chrome_path() -> str:
        potential_commands = ['chromium-browser', 'google-chrome',
                              'chromium', 'chrome']
        for command in potential_commands:
            installed_binary_path = _get_path_for_command(command)
            if installed_binary_path is not None:
                return installed_binary_path
        raise ValueError('No Chrome or Chromium install found.')

    def start_chrome(
            self,
            binary_path,
            port: Optional[int] = None,
            flags: Optional[List[str]] = None
    ) -> Tuple[subprocess.Popen, IO, str]:
        _port = port if port is not None else self.DEFAULT_PORT
        cmd = [
            os.path.abspath(binary_path),
            '--remote-debugging-port={}'.format(_port),
            *((self.HEADLESS_FLAGS + self.FONT_FLAGS) if flags is None
              else flags)
        ]
        log_path = tempfile.mkstemp()[1]
        log_file = open(log_path, 'w')
        return (
            subprocess.Popen(  # nosec: B603
                cmd, stdout=log_file, stderr=log_file, shell=False),
            log_file,
            log_path
        )

    def connect_to_chrome(self,
                          port: Optional[int] = None,
                          timeout: Optional[float] = None) -> ChromeApi:
        _port = port if port is not None else self.DEFAULT_PORT
        _timeout = timeout if timeout is not None else self.DEFAULT_TIMEOUT

        start_time = time.time()
        api = None
        error = None
        while not api and time.time() - start_time < _timeout:
            try:
                api = ChromeApi(
                    self.log_path, 'localhost', _port, timeout=_timeout)
            except Exception as e:
                error = e
                time.sleep(0.1)
        if not api:
            raise error
        else:
            return api

    def terminate(self):
        # first close the connection to the Chrome DevTools
        try:
            self.api.close()
        except Exception as e:
            logger.exception(e)

        # then stop the chromium process
        try:
            self.chrome_process.terminate()
            self.chrome_process.communicate()
        except Exception as e:
            try:
                logger.warning(e)
                os.kill(self.pid, signal.SIGKILL)
            except Exception as e_:
                logger.exception(e_)
        finally:
            self.chrome_process = None

        # then close the log file
        try:
            self.log_file.close()
            os.remove(self.log_path)
        except Exception as e:
            logger.exception(e)

        self.terminated = True
