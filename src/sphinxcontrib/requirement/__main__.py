
# python -m sphinxcontrib.requirement -i <file> -o <file> [default: <input>.new] --doc <str> --start-serial <int>
# Example:
#   python -m sphinxcontrib.requirement -i doc/requirement1.rst -o doc/requirement1.rst.new --doc AA --start-serial 900
#    diff -w doc/requirement1.rst doc/requirement1.rst.new

import sys
import logging
import argparse
import re

rReq = re.compile(r'(?P<req>.. req:req::.*)\n(?P<options>(    :(?P<optionkey>\w+):(?P<optionvalue>.*)\n)+)', re.UNICODE)
rOption = re.compile(r'    :(?P<optionkey>\w+):(?P<optionvalue>.*)\n', re.UNICODE)

# _____________________________________________________________________________
def process(args):
    serial = args.start_serial
    buf = args.input.read()
    def fReq(mo_req, ctx=locals()):
        serial = ctx['serial']
        for mo_opt in rOption.finditer(mo_req['options']):
            logging.debug(mo_opt['optionkey'] + '/' + mo_opt['optionvalue'])
            if mo_opt['optionkey'] == 'reqid' or mo_opt['optionkey'] == 'csv-file':
                break
        else:
            logging.info('Found one requirement with no ID: [{}]'.format(mo_req['req'][12:].strip()))
            nreqid = args.req_idpattern.format(**dict(doc=args.doc, serial=serial))
            ctx['serial'] = serial + 1
            return mo_req['req']+'\n    :reqid: '+nreqid+'\n'+mo_req['options']
        return mo_req['req']+'\n'+mo_req['options']
    buf = rReq.sub(fReq, buf)

    if args.output == '-':
        sys.stdout.write(buf)
    elif args.output == '=':
        args.input.close()
        with open(args.input.name, 'w', encoding='utf-8') as f:
            f.write(buf)
    else:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(buf)

# _____________________________________________________________________________
def main(argv=sys.argv[1:]):

    parser = argparse.ArgumentParser(description='Preprocessing of ReST files with requirements')
    parser.add_argument("-i", "--input", dest='input', type=argparse.FileType('rt', encoding='utf-8'), help="Input file")
    parser.add_argument("-o", "--output", dest='output', default='-', type=str, help="Output file")
    parser.add_argument("-s", "--start-serial", default=1, dest='start_serial', type=int, help="First value of the serial number")
    parser.add_argument("-d", "--doc", default='0', dest='doc', type=str, help="Document ID")
    parser.add_argument("-p", "--req_idpattern", default='REQ-{doc}{serial:03d}', dest='req_idpattern', type=str, help="Requirement ID pattern")

    parser.add_argument("-l", "--loglevel", default='INFO', dest='loglevel', help="Log level")
    parser.add_argument("-f", "--logfile", default=None, dest='logfile', help="Log file")

    args = parser.parse_args(argv)

    h = logging.StreamHandler(sys.stdout)
    f = logging.Formatter('%(asctime)-15s %(levelname)s - %(message)s')
    h.setFormatter(f)
    h.setLevel(logging.getLevelNamesMapping()[args.loglevel])
    logging.basicConfig(force=True,
                        level=logging.getLevelNamesMapping()[args.loglevel],
                        handlers=[h])
    if args.logfile:
        fh = logging.handlers.RotatingFileHandler(args.logfile, maxBytes=1000000, backupCount=20)
        fh.setLevel(logging.getLevelNamesMapping()[args.loglevel])
        fh.setFormatter(f)
        logging.getLogger().addHandler(fh)

    if args.input.name == args.output:
        logging.error('You must specify different input/output files')
        return

    logging.info('Starting')
    process(args)
    logging.info('Done')

if __name__ == '__main__':
    main()
