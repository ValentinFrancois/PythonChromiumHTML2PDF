from typing import Optional, Callable
import subprocess

from PythonChromiumHTML2PDF.chrome_process import ChromeProcess
from PythonChromiumHTML2PDF.chrome_api import ChromeApi, ChromeApiCallback


def _get_path_for_command(command: str) -> Optional[str]:
    try:
        return subprocess.check_output(['which', command])
    except Exception:
        return None


def print_to_pdf(
    binary_path: Optional[str] = None,
    input_html_path: Optional[str] = None,
    input_url: Optional[str] = None,
    output_pdf_path: Optional[str] = None,
    timeout: Optional[int] = None,
    callback: Optional[ChromeApiCallback] = None,

) -> str:
    if binary_path is None:
        installed_chromium_path = _get_path_for_command('chromium-browser')
        installed_chrome_path = _get_path_for_command('google_chrome')
        if not (installed_chromium_path or installed_chrome_path):
            raise ValueError(f'No Chrome or Chromium install found.')
        else:
            binary_path = installed_chromium_path or installed_chrome_path

    with ChromeProcess(binary_path) as chrome_api:
        try:
            return chrome_api.print_to_pdf(
                input_html_path=input_html_path,
                input_url=input_url,
                output_pdf_path=output_pdf_path,
                timeout=timeout,
                callback=callback
            )
        except Exception:
            logs = chrome_api.get_chromium_logs()
            self.base_logger.error(
                f'An error happened. Chromium logs:\n{logs}')
            raise


if __name__ == '__main__':
    print_to_pdf(input_url='http://example.org')