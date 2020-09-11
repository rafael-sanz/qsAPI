import sys
from qsAPI import QRS, QPS, __version__


def main():
    '''
    Alternative command line invocation, examples:
        qsAPI -s myServer -c dir/client.pem -Q QRS AppDictAttributes
        qsAPI -s myServer -c dir/client.pem -Q QRS -v INFO AppExport d8b120d7-a6e4-42ff-90b2-2ac6a3d92233 
        python -m qsAPI -s myServer -c dir/client.pem -Q QRS -v INFO AppReload d8b120d7-a6e4-42ff-90b2-2ac6a3d92233

    '''
    from argparse import ArgumentParser
    import inspect
    from pprint import pprint

    parser = ArgumentParser(description='qsAPI for QlikSense')
    parser.add_argument('-s', dest='server', required=True,
                        help='server hostname | hostname:port | https://hostname:port')
    parser.add_argument('-u', dest='user', required=False,
                        default='internal\\sa_repository', help='user in domain\\userid format.')
    parser.add_argument('-p', dest='password', required=False,
                        default=None, help='password credential (NTLM)')
    parser.add_argument('-c', dest='certificate', required=False,
                        help='path to client.pem certificate.')
    parser.add_argument('-P', dest='vproxy', required=False,
                        help='virtual proxy preffix if needed.')
    parser.add_argument(
        "-Q", dest="api", choices=['QPS', 'QRS'], default='QRS', required=True, help="service API")
    parser.add_argument("-v", dest="verbose", choices=[
                        'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO', help="set verbosity level")
    parser.add_argument('--version', action='version',
                        version='tools {}'.format(__version__))
    parser.add_argument(dest='method', nargs='+',
                        help='API method to call and arguments')

    # Process arguments
    args = parser.parse_args()
    Q = QPS if args.api == 'QPS' else QRS

    if not (bool(args.password) != bool(args.certificate)):
        print('ERROR: One and only one authentication method must be provided (password or certificate)')
        sys.exit(-1)

    user = args.user.replace('\\\\', '\\').split('\\')
    user.append(args.password)
    qr = Q(proxy=args.server, vproxy=args.vproxy,
           certificate=args.certificate, user=user, verbosity=args.verbose)
    m = [x for x, y in inspect.getmembers(Q) if not x.startswith('_')]

    cmd = args.method[0]
    if cmd not in m:
        print('ERROR: "{}" is not a method of {}, expected=> {}'.format(
            cmd, args.api, m))
        sys.exit(-1)

    pprint(getattr(qr, cmd)(*args.method[1:]))
    sys.exit(0)


if __name__ == "__main__":
    main()
