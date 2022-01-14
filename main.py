import sys
import json

from PythonChromiumHTML2PDF.print_to_pdf import print_to_pdf


def main():
    if len(sys.argv) < 2:
        raise ValueError('Expects a JSON print config as argument')
    json_print_config = sys.argv[1]
    try:
        print_config = json.loads(json_print_config)
    except Exception as e:
        raise ValueError(f'Error parsing JSON print config: {e}')
    print_to_pdf(**print_config)


if __name__ == '__main__':
    print_config = dict(
        binary_path='/usr/bin/google-chrome',
        input_url='http://example.org',
        screen_width=1080,
        paperWidth=8.27,
        paperHeight=11.7,
        marginTop=0,
        marginBottom=0,
        marginLeft=0,
        marginRight=0,
        printBackground=True
    )
    sys.argv.append(json.dumps(print_config))
    main()
