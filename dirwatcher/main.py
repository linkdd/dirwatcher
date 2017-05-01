# -*- coding: utf-8 -*-

from dirwatcher.core import DirectoryWatcher
from argparse import ArgumentParser


def main():
    parser = ArgumentParser()
    parser.add_argument('-d', '--directory', required=True, nargs=1)
    parser.add_argument('-c', '--command', required=True, nargs=1)

    args = parser.parse_args()

    directory = args.directory[0]
    command = args.command[0]

    dw = DirectoryWatcher(directory, command)
    dw.reloader()


if __name__ == '__main__':
    main()
