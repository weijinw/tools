#!/usr/bin/env python
import argparse
import json
import sys
import datetime


parser = argparse.ArgumentParser(description='Parse json logs')
parser.add_argument('--file-name', '-f',
                    dest='log_file',
                    type=str,
                    default='',
                    help="the log file")
parser.add_argument('--num-lines', '-n',
                    dest='num',
                    type=int,
                    default=-1,
                    help='number of lines to be parsed')
parser.add_argument('--keys', '-k',
                    dest='keys',
                    type=str,
                    default='',
                    help='keys to be parsed, use comma to '
                         'separate multiple keys')

args = parser.parse_args()


def parse_json_log(line):
    try:
        return json.loads(line)
    except Exception as ex:
        return None


def parse_instant(instant):
    try:
        ts = json.loads(instant)
        return datetime.datetime.fromtimestamp(
            ts['epochSecond'] + ts['nanoOfSecond'] / 1000000000)
    except Exception as ex:
        return None


def get_level(body):
    for key in ['level']:
        if key in body:
            return body[key]
    return '-'


def get_timestamp(body):
    if 'instant' in body:
        return parse_instant(body['instant'])

    for key in ['ts', 'timestamp', 'time', 'date']:
        if key in body:
            return body[key]
    return '-'


def get_message(body):
    for key in ['msg', 'message', 'log']:
        if key in body:
            return body[key]
    return '-'


def print_keys(body):
    print(list(body.keys()))


def print_line(body, keys):
    line = []
    if keys:
        for key in keys:
            line.append(body.get(key))
    else:
        line.append(get_timestamp(body))
        line.append(get_level(body))
        line.append(get_message(body))
    print(' '.join([str(field) for field in line]))


def parse_log_file(log_file, num, keys=None):
    parsed_lines = 0
    with open(log_file, 'r') as lf:
        for line in lf:
            body = parse_json_log(line)
            if parsed_lines == 0:
                print_keys(body)
            print_line(body, keys)

            parsed_lines += 1
            if 0 < num <= parsed_lines:
                break


def parse_stdin(num, keys=None):
    parsed_lines = 0
    for line in sys.stdin:
        body = parse_json_log(line)
        if parsed_lines == 0:
            print_keys(body)
        print_line(body, keys)

        parsed_lines += 1
        if 0 < num <= parsed_lines:
            break


if __name__ == '__main__':
    if not args.log_file and sys.stdin.isatty():
        print('No input')
        exit(0)

    keys = [key for key in args.keys.split(',') if key]
    if args.log_file:
        parse_log_file(args.log_file, args.num, keys)
    else:
        parse_stdin(args.num, keys)
