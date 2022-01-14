"""Defines the main function of this package, that wraps around the
`ChromeProcess` and `ChromeApi` classes and deals with all the arguments.
"""

import os
from typing import Optional
import logging

from PythonChromiumHTML2PDF.chrome_process import ChromeProcess
from PythonChromiumHTML2PDF.chrome_api import ChromeApi, ChromeApiCallback


logging.basicConfig(format='%(levelname)s %(module)s:%(lineno)s %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


DEFAULT_PRINT_OPTIONS = dict(
    paperWidth=8.27,  # inches (= 21.0 cm)
    paperHeight=11.7,  # inches (=29.7 cm)
    marginTop=0,
    marginBottom=0,
    marginLeft=0,
    marginRight=0,
    printBackground=True
)

PAGE_DEFAULT_RESOLUTION = 96  # dpi


def print_to_pdf(
    binary_path: Optional[str] = None,
    input_html_path: Optional[str] = None,
    input_url: Optional[str] = None,
    output_pdf_path: Optional[str] = None,
    timeout: Optional[int] = None,
    callback: Optional[ChromeApiCallback] = None,
    screen_width: Optional[int] = None,
    **print_options
) -> str:
    """
    :param binary_path:
        path to the Chromium/Chrome browser binary.
        If not provided, will try to get an installed Chromium/Chrome browser.
    :param input_html_path:
        path to a HTML file on the disk to convert
    :param input_url:
        address of a remote page to convert (must include the http(s):// part)
    :param output_pdf_path:
        output PDF path.
        - if `input_html_path` is passed:
            defaults to the same filename with '.pdf' instead of '.html'.
        - if `input_url` is passed:
            defaults to 'result.pdf'
    :param timeout:
        timeout for all wait operations (connecting to the browser, loading
        the input page, waiting for a CSS selector...)
    :param callback:
        see `ChromeApiCallback` docstring
    :param screen_width:
        Width in pixels of the area you want to capture in the PDF.
        (From what I understood, CDP's Page.printToPDF() assumes a resolution
        of 96 DPI when `scale` is set to 1 (default).
        The width of the captured area should then be  96 * `scale` *
        `paperWidth`, e.g. for a A4 sheet (8.27 in), the default width of
        the captured area would be 96 * 1 * 8.27 = 794 pixels.)
        If `screen_width` is passed alongside to `paperWidth`, `scale` will
        be automatically calculated to fit exactly `screen_width` pixels into
        the PDF page.
    :param print_options:
        All the options that can be passed to CDP's Page.printToPDF(),
        see https://chromedevtools.github.io/devtools-protocol/tot/Page
            /#method-printToPDF
        some default values are overwritten by `DEFAULT_PRINT_OPTIONS`
    :return:
        Path of the output PDF
    """

    _print_options = DEFAULT_PRINT_OPTIONS.copy()
    _print_options.update(print_options)

    if screen_width is not None:
        page_width_inches = _print_options['paperWidth']
        scale = page_width_inches/(screen_width/PAGE_DEFAULT_RESOLUTION)
        _print_options['scale'] = scale

    with ChromeProcess(binary_path) as chrome_api:
        chrome_api: ChromeApi
        try:
            _output_pdf_path = chrome_api.print_to_pdf(
                input_html_path=input_html_path,
                input_url=input_url,
                output_pdf_path=output_pdf_path,
                timeout=timeout,
                callback=callback,
                **_print_options
            )
            logger.info(f'Converted {input_html_path or input_url} to PDF '
                        f'at {os.path.abspath(_output_pdf_path)}')
            return _output_pdf_path
        except Exception:
            logs = chrome_api.get_chromium_logs()
            logger.error(f'An error happened. Chromium logs:\n{logs}')
            raise
