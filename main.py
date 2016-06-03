import argparse
from bread.bread_server import app


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Bread server')

    parser.add_argument('-p', '--port', type=int, help='The server port', default=5000)
    # parser.add_argument('--logdir', type=str, help='The log directory', default=r'/var/log/mmp_server')

    args = vars(parser.parse_args())

    # Use warning because we do want to log this
    host = args.get('host', '0.0.0.0')
    port = args['port']

    app.logger.warning("")
    app.logger.warning("***Starting application ({}:{})***".format(host, port))

    # Running the built-in http server is only for development purposes, for production:
    # use e.g. nginx + tornado (or Gunicorn, Gevent, ...).
    # host: when set, the debug app is visible in the network
    # debug = True: reloads the test server on code changes. Can be disabled by setting use_reloader to false.
    # app.run(host='0.0.0.0', debug=app.config['DEBUG'], use_reloader=False)
    app.run(host=host, debug=app.config['DEBUG'], port=port)
    # app.run(debug=app.config['DEBUG'])
