#!/usr/bin/env python3

"""
Created on Mon May  8 14:04:16 2023
@author: Scover
"""

from functools import partial
from random_header_generator import HeaderGenerator
from sys import stdout, stderr
from time import sleep
import argparse as ap
import csv
import datetime as dt
import pytz
import random
import re
import requests

# Features to avoid detection
# - Random header - changes randomly or on error
# - Random wait time
# - Fetch other pages once in a while (site homepage...)
# - Fetch games in a random order in fixed-size "chunks"

CHANCE_COFFEE_BREAK = .003217  # 0.3217%
CHANCE_DISTRATION_URL = .15554  # 15.554%
CHANCE_HEADER_CHANGE = .05869  # 5.869%
MAX_RETRIES = 1000
REQUEST_TIMEOUT = 30
WAIT_MAX = 20
WAIT_MIN = 3

CRASH_PATTERN = 'Crashed @(\d+,?\d*\.\d\d)x'
GAME_PLAYER_BET_PATTERN = '<td> ([,\d]+) Ethos'
GAME_TIME_FMT = '%a %b %d %Y %H:%M:%S'
GAME_TIMEZONE = pytz.timezone('Europe/Paris')
HEADER_GENERATOR = HeaderGenerator()
TIME_PATTERN = '<p class=\"text-muted mb-0\">\d+[a-zA-Z ]+ ago on ([a-zA-Z :\d]+) GMT'
URL_PREFIX = 'http://www.ethercrash.io/game/'

DISTRACTION_URLS = (
    'https://www.ethercrash.io/', 'https://www.ethercrash.io/play', 'https://www.ethercrash.io/faq',
    'https://www.ethercrash.io/weekly', 'https://www.ethercrash.io/login', 'https://www.ethercrash.io/leaderboard',
    'https://www.ethercrash.io/register', 'https://www.ethercrash.io/stats', 'https://www.ethercrash.io/changelog',
    'https://www.ethercrash.io/leaderboard?by=net_asc', 'https://www.ethercrash.io/leaderboard?by=net_desc',
    'https://www.ethercrash.io/xmas', 'https://www.ethercrash.io/contact', 'https://www.ethercrash.io/account-recovery',
    'https://www.ethercrash.io/forgot-password', 'https://www.ethercrash.io/?ref=sxiii', 'https://www.ethercrash.io/account',
    'https://bustabit.com/', 'https://www.ethercrash.io/ethercrash.io-TOS.pdf')

log = lambda *args, **kws: None

header = HEADER_GENERATOR()


def main():
    global log, header

    parser = ap.ArgumentParser(description='Scrape ethercrash game logs to stdout')

    parser.add_argument('id_start', type=int,
                        help='start id (inclusive). will scrape ids in decreasing order until id_end is reached')
    parser.add_argument('id_end', type=int,
                        help='end id (exclusive)')
    parser.add_argument('-c', '--chunk-size', type=int, default=100,
                        help='size of the chunk of game IDs to shuffle')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='show verbose output')
    parser.add_argument('--header', action='store_true',
                        help='write a header row')
    parser.add_argument('--dry-run', action='store_true',
                        help="dry run: explain what is done")

    args = parser.parse_args()

    if args.id_start <= args.id_end:
        parser.error('id_start must be greater than id_end')
    if args.chunk_size <= 0:
        parser.errror('chunk-size must be positive')

    if args.verbose or args.dry_run:
        log = partial(print, file=stderr)

    scrape = scrape_dry_run if args.dry_run else scrape_url

    writer = csv.writer(stdout)

    if args.header:
        writer.writerow(('id', 'crash', 'timestamp', 'bet_sum', 'player_count'))  # write header row
        log('Header row written.')

    done_count = 0
    for chunk in range(args.id_start, args.id_end, -args.chunk_size):
        log('Starting chunk', chunk)
        results = []
        chunk_ids = range(chunk, max(args.id_end, chunk - args.chunk_size), -1)
        try:
            for id in random.sample(chunk_ids, len(chunk_ids)):
                # start - end = done + remaining (chunk done/chunk size)
                log(f'{args.id_start}-{args.id_end}={done_count}+{args.id_start - args.id_end - done_count} ({len(results)}/{args.chunk_size}): {id}: ', end='')
                done_count += 1

                html = scrape(f'{URL_PREFIX}{id}')

                crash = get_crash(html)
                timestamp = get_timestamp(html)
                player_count, bet_sum = get_player_stats(html)

                results.append((id, crash, timestamp, bet_sum, player_count))

                log(f'on {timestamp}, {player_count} betted {bet_sum}, crashed at {crash}, ', end='')

                pause(get_wait_time(WAIT_MIN, WAIT_MAX))
                #pause(.5)

                if test(CHANCE_COFFEE_BREAK):
                    log('COFFEE BREAK!', end=' ')
                    pause(random.uniform(.75, 1.25) * 600)
                if test(CHANCE_DISTRATION_URL):
                    url = random.choice(DISTRACTION_URLS)
                    log('DISTRACTION URL!', url)
                    requests.get(url, headers=header, timeout=REQUEST_TIMEOUT)
                if test(CHANCE_HEADER_CHANGE):
                    log('HEADER CHANGE!')
                    header = HEADER_GENERATOR()
        finally:
            results = sorted(results, key=lambda row: row[0], reverse=True)
            # if any error or Ctrl+C termination occurs, write the incomplete results to console
            if len(results) != args.chunk_size:
                log('INCOMPLETE CHUNK OF SIZE', len(results))
                for r in results:
                    log(*r, sep=',')
            else:
                log('Writing', len(results), 'rows...')
                writer.writerows(results)  # write rows sorted by id descending


def scrape_url(url: str) -> str:
    global header

    for tryNo in range(1, MAX_RETRIES+1):
        res = requests.get(url, headers=header, timeout=REQUEST_TIMEOUT)
        if res.ok:
            break
        log(f'got {res.status_code} for {res.url} (header "{header}"), retry {tryNo}')
        pause(random.uniform(.75, 1.25) * tryNo**2)  # pause for longer and longer on each try
        header = HEADER_GENERATOR()  # retry with a new header
    else:
        res.raise_for_status()
    res.encoding = 'utf-8'
    return res.text


def get_timestamp(html: str) -> int:
    """Get the unix timestamp of the game"""
    match = re.search(TIME_PATTERN, html)
    assert match is not None, f'Game time not found in {html}'

    date_string = match.group(1)
    parsed_datetime = dt.datetime.strptime(date_string, GAME_TIME_FMT)
    aware_datetime = GAME_TIMEZONE.localize(parsed_datetime)

    # Convert the timezone-aware datetime object to a Unix timestamp
    return int(aware_datetime.timestamp())


def scrape_dry_run(url: str) -> str:
    """ Dry run scraping. """
    log('scraping', url, end=': ')
    with open('sample_game_page.html', 'r') as f:
        text = f.read()
    return text


def get_crash(html: str):
    """Get the crash value of the game"""
    match = re.search(CRASH_PATTERN, html)
    assert match is not None, f'Crash not found in {html}'
    return parse(float, match.group(1))


def get_player_stats(html: str) -> tuple[int, int]:
    """Get the player count and sum of all player's bets in Ethos"""
    matches = re.findall(GAME_PLAYER_BET_PATTERN, html)
    return len(matches), sum(parse(int, m) for m in matches)


def pause(time: float):
    log('pause for', time)
    sleep(time)


def parse(num_type: type, s: str) -> float:
    return num_type(s.replace(',', ''))


def get_wait_time(min: float, max: float) -> float:
    r = random.random() * random.random()
    return (max - min) * r + min


def test(proba: float) -> bool:
    return random.random() < proba


if __name__ == '__main__':
    main()
