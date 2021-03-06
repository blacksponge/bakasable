import random
import logging
import sys
import argparse

import bakasable
import bakasable.config
import bakasable.debug


logger = logging.getLogger(__name__)


def setup_logger():
    root_logger = logging.getLogger()
    ch = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s#%(lineno)d - %(message)s')
    ch.setFormatter(formatter)
    root_logger.addHandler(ch)

    logging.TRACE = 9
    logging.addLevelName(logging.TRACE, 'TRACE')

    def trace(self, message, *args, **kwargs):
        if self.isEnabledFor(logging.TRACE):
            self._log(logging.TRACE, message, args, **kwargs)

    logging.Logger.trace = trace


def main():
    setup_logger()
    config = bakasable.config.get_config()

    parser = argparse.ArgumentParser(
        prog='bakasable',
        description=' Peer to peer multiplayer sandbox game based on NDN.')

    parser.add_argument(
        '--host', '-H',
        metavar='<nfd_host>',
        help='Address of the host to connect to.',
        default=config.get('main', 'host', fallback='localhost'))

    parser.add_argument(
        '--game', '-g',
        metavar='<game_id>',
        help='Set the game id to connect to.',
        default=config.getint(
            'main', 'game_id', fallback=random.getrandbits(64)),
        type=int)

    parser.add_argument(
        '--peer', '-p',
        metavar='<peer_id>',
        help='Set the peer id.',
        default=config.getint(
            'main', 'peer_id', fallback=random.getrandbits(64)),
        type=int)

    parser.add_argument(
        '--pseudo', '-P',
        metavar='<pseudo>',
        help='Set player pseudo.',
        default=config.get('main', 'pseudo', fallback='toto'))

    parser.add_argument(
        '--disable-graphics', '-d',
        help='Disable graphical interface',
        action='store_true',
        default=not config.getboolean('main', 'graphics', fallback=True))

    parser.add_argument(
        '--debug', '-D',
        help='Display debug tool',
        action='store_true',
        default=config.getboolean('main', 'debug_tool', fallback=False))

    parser.add_argument(
        '-v',
        action='count',
        help='Log verbosity from 0 to 5, default to 3')

    args = parser.parse_args()

    loglevels = [logging.CRITICAL,
                 logging.ERROR,
                 logging.WARNING,
                 logging.INFO,
                 logging.DEBUG,
                 logging.TRACE]
    logging.getLogger().setLevel(loglevels[
        config.getint('main', 'log_verbosity', fallback=3)
        if args.v is None else args.v])

    logger.info('Starting app with game_id=%s and peer_id=%s',
                args.game, args.peer)

    my_app = bakasable.App(args.host,
                           args.game,
                           args.pseudo,
                           args.peer,
                           not args.disable_graphics)

    if args.debug:
        logger.info('Starting debug tool')
        debug_tool = bakasable.debug.DebugTool(my_app)

    my_app.run()

    if args.debug:
        debug_tool.root.quit()


if __name__ == '__main__':
    main()
