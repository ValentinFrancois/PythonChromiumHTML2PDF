import argparse
import json
import sys

from PythonChromiumHTML2PDF.print_to_pdf import print_to_pdf


CDP_LINK = 'https://chromedevtools.github.io/devtools-protocol/tot/Page/' \
           '#method-printToPDF'


def main(argv):
    parser = argparse.ArgumentParser()

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('-f', '--file', type=str,
                             help='Input HTML file path')
    input_group.add_argument('-l', '--link', type=str,
                             help='Link to a HTML web page')

    parser.add_argument('-t', '--target', type=str,
                        help='Output PDF file path')

    parser.add_argument('-o', '--options', type=str, default='{}',
                        help=f'JSON print options (see {CDP_LINK})')

    args = parser.parse_args(argv)

    try:
        print_config = json.loads(args.options)
        if args.file:
            print_config['input_html_path'] = args.file
        if args.link:
            print_config['input_url'] = args.link
        if args.target:
            print_config['output_pdf_path'] = args.target
    except Exception as e:
        print(args.options)
        raise ValueError(f'Error parsing JSON print options: {e}')
    print_to_pdf(**print_config)


if __name__ == '__main__':
    main(sys.argv[1:])
