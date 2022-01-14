import unittest
import os
import subprocess
import tempfile
import time

from PythonChromiumHTML2PDF.chrome_process import ChromeProcess
from PythonChromiumHTML2PDF.chrome_api import ChromeApi


class TestPrintToPDF(unittest.TestCase):
    """Assumes """

    def setUp(self) -> None:
        self.html_file = tempfile.mkstemp(suffix='.html')[1]

    def tearDown(self) -> None:
        try:
            os.remove(self.html_file)
        except Exception:
            pass

    @staticmethod
    def _list_processes():
        stdout = subprocess.getoutput('ps -o ppid,pid,args')
        processes = []
        for line in stdout.splitlines():
            splitted = line.split(' ')
            ppid, pid = splitted[:2]
            cmdline = ' '.join(splitted[2:])
            processes.append([ppid, pid, cmdline])
        return processes

    def test_find_installed_chrome_path(self):
        self.assertTrue(
            os.path.isfile(ChromeProcess.find_installed_chrome_path()))

    def test_context_manager(self):
        with ChromeProcess() as chrome_api:
            chrome_api: ChromeApi
            # chrome is running now
            process_names = [p[2] for p in self._list_processes()]
            print(process_names)
            self.assertTrue(
                any(['chrome' in p or 'chromium' in p for p in process_names]))
            log_file = chrome_api.log_file
            self.assertTrue(os.path.isfile(log_file))
        # chrome has been stopped
        time.sleep(1)
        process_names = [p[2] for p in self._list_processes()]
        self.assertFalse(
            any(['chrome' in p or 'chromium' in p for p in process_names]))
        self.assertFalse(os.path.isfile(log_file))

    def test_get_chromium_logs(self):
        with open(self.html_file, 'w') as html:
            html.write('<html><body>Hello World</body></html>')
        with ChromeProcess() as chrome_api:
            chrome_api: ChromeApi
            chrome_api.open_file(self.html_file)
            logs = chrome_api.get_chromium_logs()
        self.assertIn('DevTools listening on ws://', logs)

    def test_wait_for_selector(self):
        with open(self.html_file, 'w') as html:
            html.write(
                '<html><body><h2 id="mock">Hello World</h2></body></html>')
        with ChromeProcess() as chrome_api:
            chrome_api: ChromeApi
            chrome_api.open_file(self.html_file)
            self.assertTrue(chrome_api.wait_for_selector('#mock') > 1)
            with self.assertRaises(ValueError):
                chrome_api.wait_for_selector('#nope')
