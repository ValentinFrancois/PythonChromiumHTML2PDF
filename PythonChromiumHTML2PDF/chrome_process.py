from typing import Optional, List, Tuple, IO

import os
import tempfile
import signal
import time
from subprocess import Popen  # nosec: B404
import logging

from PythonChromiumHTML2PDF.chrome_api import ChromeApi


logger = logging.getLogger(__name__)


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
                 binary_path: str,
                 port: Optional[int] = None,
                 timeout: Optional[float] = None,
                 flags: Optional[List[str]] = None):
        return_values = self.start_chrome(binary_path, port, flags)
        self.chrome_process: Popen = return_values[0]
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

    def start_chrome(
            self,
            binary_path,
            port: Optional[int] = None,
            flags: Optional[List[str]] = None) -> Tuple[Popen, IO, str]:
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
            Popen(cmd, stdout=log_file, stderr=log_file, shell=False),
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
            logger.error(e)

        # then stop the chromium process
        try:
            self.chrome_process.terminate()
            self.chrome_process.communicate()
        except Exception as e:
            try:
                logger.warning(e)
                os.kill(self.pid, signal.SIGKILL)
            except Exception as e_:
                logger.error(e_)
        finally:
            self.chrome_process = None

        # then close the log file
        try:
            self.log_file.close()
            os.remove(self.log_path)
        except Exception as e:
            logger.error(e)

        self.terminated = True
