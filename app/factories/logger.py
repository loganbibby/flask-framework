import logging
import os

def setup_logging(logger=None, debug=True, logfile='messages.log'):
    if logger is None:
        logger = logging.getLogger('main')

    log_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logger.setLevel(logging.DEBUG)

    logger.handlers = []

    if debug:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(log_formatter)
        stream_handler.setLevel(logging.DEBUG)
        logger.addHandler( stream_handler )

    file_handler = logging.FileHandler('%s/%s' % (os.getcwd(), logfile))
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.DEBUG if debug else logging.INFO)
    logger.addHandler(file_handler)

    return logger

def init_app(app):
    setup_logging( app.logger, app.debug, app.config['LOGFILE'] )
