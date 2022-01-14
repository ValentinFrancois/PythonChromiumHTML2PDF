"""Defines common manipulations of a browser tab via a `ChromeApi` wrapper
class that internally uses the Chrome DevTools Protocol (CDP).

`ChromeApi` inherits from the `ChromeInterface` class of the PyChromeDevTools
package, which handles the low-level communication with the browser through a
websocket.
"""

from typing import Optional, Callable, Dict

import os
import time
import base64
import re

from PyChromeDevTools import ChromeInterface


class ChromeApiCallback(Callable):
    """Defines a way to execute extra steps between opening the HTML page
    and saving it to PDF.

    If passed to `ChromeApi.print_to_pdf(...)`, such `ChromeApiCallback`
    will be called with `self` as argument right after opening the input page.
    It can then use the methods of `ChromeApi` to perform extra actions like
    waiting for a specific CSS selector, executing JavaScript code, etc.

    The return value is a dict containing optional arguments to the
    `Page.printToPDF` function of the CDP. This leaves the possibility to
    override some arguments dynamically depending on the content of the page
    (for instance the `scale` argument could be calculated from `body.width`).
    """
    def __call__(self, chrome_api: 'ChromeApi') -> Dict[str, object]:
        # use the chrome_api for custom actions on the page
        return {}


class ChromeApi(ChromeInterface):

    def __init__(self, log_file: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.version = self.get_browser_version()
        self.log_file = log_file

    def _dev_tools_protocol_error(self, e: Exception, response):
        raise RuntimeError(
            f'{e.__class__.__name__}: {e}'
            f'\nResponse from Chrome/Chromium (version {self.version}):'
            f'\n{response}')

    def get_browser_version(self):
        return_value, response = self.Browser.getVersion()
        try:
            version_str = return_value['result']['product']
        except Exception as e:
            self.version = 'unknown'
            self._dev_tools_protocol_error(e, response)

        version = re.findall('([0-9\\.]+)|$', version_str)[0]
        return version

    def open_url(self, url, timeout: Optional[int] = None):
        self.Page.navigate(url=url)
        self.wait_event('Page.loadEventFired',
                        timeout=timeout or self.timeout)

    def open_file(self, html_path, timeout: Optional[int] = None):
        html_abs_path = os.path.abspath(html_path)
        # chrome will display a blank page if the file doesn't exit
        # we have to detect the issue beforehand to raise an error.
        if not os.path.isfile(html_abs_path):
            raise FileNotFoundError(html_abs_path)
        self.open_url(f'file://{html_abs_path}', timeout)

    def wait_for_selector(self,
                          selector: str,
                          timeout: Optional[int] = None) -> int:
        _timeout = timeout if timeout is not None else self.timeout
        start_time = time.time()
        while time.time() - start_time < _timeout:
            try:
                node_id = self.get_node_id_for_selector(selector)
                return node_id
            except ValueError:
                time.sleep(0.1)
        raise ValueError(
           f'Timeout reached without finding selector "{selector}"')

    def get_node_id_for_selector(self, selector: str) -> int:
        self.DOM.enable()
        root_node_id = self.get_root_node_id()
        return_value, response = self.DOM.querySelector(nodeId=root_node_id,
                                                        selector=selector)
        try:
            queried_node_id = return_value['result'].get('nodeId', 0)
        except Exception as e:
            self._dev_tools_protocol_error(e, response)

        if queried_node_id < 1:
            raise ValueError(f'Selector {selector} not found')
        return queried_node_id

    def get_root_node_id(self) -> int:
        self.DOM.enable()
        return_value, response = self.DOM.getDocument()
        try:
            root_node_id = return_value['result']['root']['nodeId']
            return root_node_id
        except Exception as e:
            self._dev_tools_protocol_error(e, response)

    def get_page_html(self) -> str:
        self.DOM.enable()
        root_node_id = self.get_root_node_id()
        return_value, response = self.DOM.getOuterHTML(nodeId=root_node_id)
        try:
            html = return_value['result']['outerHTML']
            return html
        except Exception as e:
            self._dev_tools_protocol_error(e, response)

    def evaluate_javascript(self, javascript: str, expected_return_value=None):
        self.Runtime.enable()
        return_value, response = self.Runtime.evaluate(expression=javascript)
        try:
            value = return_value['result']['result']['value']
            if expected_return_value is not None:
                if value != expected_return_value:
                    raise ValueError(
                        f"Expected return value '{expected_return_value}',"
                        f"got {value}")
        except Exception as e:
            self._dev_tools_protocol_error(e, response)

    def print_to_pdf(self,
                     input_html_path: Optional[str],
                     input_url: Optional[str],
                     output_pdf_path: Optional[str],
                     timeout: Optional[int] = None,
                     callback: Optional[ChromeApiCallback] = None,
                     **kwargs) -> str:
        """**kwargs: optional args for the Page.printToPDF() function
        """
        self.Network.enable()
        self.Page.enable()

        if not (input_url or input_html_path):
            raise ValueError(
                '`input_html_path` or `input_url` must be provided.')

        if input_url and input_html_path:
            raise ValueError(
                '`input_html_path` and `input_url` cannot be provided '
                'together.')

        if output_pdf_path is None:
            if input_url:
                output_pdf_path = 'result.pdf'
            else:
                output_pdf_path = '{}.pdf'.format(
                    os.path.splitext(input_html_path)[0])

        if input_url:
            self.open_url(input_url, timeout)
        else:
            self.open_file(input_html_path, timeout)

        # run the optional callback function e.g. to wait for specific selector
        if callback is not None:
            if isinstance(callback, type):
                callback = callback()
            extra_args: Dict[str, object] = callback(self)
            kwargs.update(extra_args)

        # force rendering the page - prevents potential bugs with font display
        self.Page.captureScreenshot()

        return_value, response = self.Page.printToPDF(
            transferMode='ReturnAsBase64',
            **kwargs
        )

        try:
            data = return_value['result']['data']
            if not data:
                raise ValueError('PDF data is empty')
        except Exception as e:
            self._dev_tools_protocol_error(e, response)

        with open(output_pdf_path, 'wb') as pdf:
            pdf.write(base64.b64decode(data))

        return output_pdf_path

    def get_chromium_logs(self) -> str:
        with open(self.log_file, 'r') as f:
            return f.read()
