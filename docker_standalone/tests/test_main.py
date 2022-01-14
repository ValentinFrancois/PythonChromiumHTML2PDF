import unittest
import os
import json
import tempfile

from command.main import main


class TestMain(unittest.TestCase):

    def test_main(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_pdf_output_path = os.path.join(temp_dir, 'output.pdf')
            print_config = dict(
                screen_width=1080,
                paperWidth=8.27,
                paperHeight=11.7,
                marginTop=0,
                marginBottom=0,
                marginLeft=0,
                marginRight=0,
                printBackground=True
            )
            args = [
                '--link=http://example.org',
                f'--target={temp_pdf_output_path}',
                f"--options={json.dumps(print_config)}"
            ]
            main(args)
            self.assertTrue(os.path.isfile(temp_pdf_output_path))

    def test_main_input_args(self):
        with self.assertRaises(BaseException):
            main([
                '--link=http://example.org',
                '--file=mock.html',
            ])
        with self.assertRaises(BaseException):
            main([
                '--target=output.pdf',
                '--options={"marginRight": 0}'
            ])

    def test_main_wrong_json_args(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_pdf_output_path = os.path.join(temp_dir, 'output.pdf')
            print_config = dict(
                input_url='http://example.org',
                output_pdf_path=temp_pdf_output_path,
            )
            wrong_json = json.dumps(print_config)[:-1]
            args = [
                '--link=http://example.org',
                f'--target={temp_pdf_output_path}',
                f'--options={wrong_json}'
            ]
            with self.assertRaises(ValueError):
                main(args)
            self.assertFalse(os.path.isfile(temp_pdf_output_path))
