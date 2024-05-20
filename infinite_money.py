#!/usr/bin/env python3

from bisect import bisect
from dataclasses import dataclass
from typing import Iterable, Callable, Sequence, Any
import statistics as stat
import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 1 ethos is 0.0000140 ETH

# -*- coding: utf-8 -*-
"""
Created on Mon May  8 11:11:18 2023

@author: Scover
"""

# Some terms
# id - the unique int id of the game
# Crash - the float value at which the game ended
# Cashout - the float value at which the player decided to bail out

# Diff : différence entre la probabilité mesurée et la probabilité minimale pour ne pas être perdant.
# Exemple : pour un cashout de 2, il faudrait gagner 1 fois sur 2 pour rentrer dans ses frais. Si la probabilité mesurée de gagner avec ce cashout est supérieure à 1/2, on sera gagnant sur un grand nombre de parties. Si elle y est inférieure, on sera perdant.
# Cashout de 2: 25% de probabilité, 50% requis:
# diff = -25%
# on ne ne gugne qu'1 fois sur 4, donc on perd 3 fois sur 4
# 1 gain amortit 1 perte, donc il reste 1 perte ou on perd.
# donc -25% signifie qu'on perd sur notre mise 1 fois sur 4
# donc la différence correspond à la probabilité de faire un bénéfice (si positif) ou une perte (si négatif) pour chaque partie.

# Gain : différence multipliée par la valeur du cashout.
# Le gain équilibre entre gagner peu souvent et gagner gros rarement.
# Le gain quantifie le bénéfice (si positif) ou la perte (si négatif) pour chaque partie.
# Dire que le gain est de 3% revient à dire qu'à chaque partie, on fait un bénéfice de 3% par rapport à la mise initiale. Donc si on mise 100, on remporte en moyenne 103.

# Goals:
# - Find out the optimal cashout based on the available game logs
#   Implementation - Use binary search (dichotomy)

P = 100
""" Precision (10^(number of digits after decimal point))"""


def main():
    CASHOUT_MIN: int = 100  # 1.00
    CASHOUT_MAX: int = 100000  # 50041.32

    with open('crashes/ictbp.csv') as file_crashes:
        reader = csv.reader(file_crashes)
        next(reader)  # Skip header row

        games = tuple(sorted((Game.create(row) for row in reader), key=lambda g: g.crash))
        print('Created games')

        # for game in create_leaderboard(games, 25, lambda g: g.player_count):
        #    print(game)

        cashouts = tuple(Cashout.create(games, x) for x in range(CASHOUT_MIN, CASHOUT_MAX + 1))
        print('Created cashouts')

        # for cashout in create_leaderboard(cashouts, 25, lambda c: c.gain):
        # print(cashout)
        # return

        fig, axes = plt.subplots(2, 1)
        plot_zero_line(axes[0])
        plot_diff(axes[0], cashouts)
        plot_gain(axes[0], cashouts)
        scatter_by(axes[1], games, ptsize=3,
                   x=lambda g: g.bet_sum, xlabel='bet sum',
                   y=lambda g: g.crash / P, ylabel='crash', yscale='log')
        plt.show()


def create_leaderboard(iterable: Iterable, size: int, key: Callable):
    """ Creates a leaderboard in decreasing order of the specified iterable """
    return sorted(iterable, key=key, reverse=True)[:size]


@dataclass(frozen=True)
class Game:
    @staticmethod
    def create(r: Sequence[str]):
        return Game(int(r[0]), int(float(r[1]) * P), int(r[2]), int(r[3]), int(r[4]))
        # return Game(int(r[0]), int(float(r[1]) * P))
    id: int
    crash: int
    timestamp: int
    bet_sum: int
    player_count: int


@dataclass(frozen=True)
class Cashout:
    value: int
    proba: float
    """Actual win probability according to the data ([0;1])"""

    @property
    def diff(self):
        """
        Difference between actual and required win probability. ([0;1])
        A higher value means more earnings
        A positive value means that we will win, negative and we will loose.
        """
        return self.proba - (P / self.value)  # Minimum win probability for a neutral gain

    @property
    def gain(self):
        """Diff times value. Scales earnings"""
        return self.diff * self.value / P

    def __repr__(self):
        return f'{self.value/P}: proba: {self.proba:.3%} diff: {self.diff:.3%} gain: {self.gain:.3%}'

    @staticmethod
    def create(games: Sequence[Game], value: int):
        # probablity : probability that crash is higher
        # = number of games where crash is higher than value / number of games
        proba = (len(games) - bisect(games, value, key=lambda g: g.crash)) / len(games)
        return Cashout(value, proba)


def plot_proba(ax, cashouts: Iterable[Cashout]):
    ax.plot([c.value/P for c in cashouts], [c.proba for c in cashouts], label="Probability")
    ax.set_xlabel("Cashout")
    ax.legend()


def plot_diff(ax, cashouts: Iterable[Cashout]):
    ax.plot([c.value/P for c in cashouts], [c.diff for c in cashouts], label="Difference")
    ax.set_xlabel("Cashout")
    ax.legend()


def plot_zero_line(ax):
    ax.axhline(y=0, color='black', linestyle='dotted')


def plot_gain(ax, cashouts: Iterable[Cashout]):
    ax.plot([c.value/P for c in cashouts], [c.gain for c in cashouts], label="Gain")
    ax.set_xlabel("Cashout")
    ax.legend()


def plot_crash_amounts(ax, games: Sequence[Game]):
    ax.hist([g.crash for g in games], bins='sqrt', log=True)
    ax.set_xlabel("Crash")
    ax.set_xscale('log')


def plot_box_crashes(ax, games: Sequence[Game]):
    crashes = [g.crash/P for g in games]
    print('median:', stat.median(crashes))
    print('mean:', stat.mean(crashes))
    print('min:', crashes[0])
    print('max:', crashes[-1])
    ax.boxplot(crashes, sym='')


def plot_bar_crash_by_player_count(ax, games: Sequence[Game]):
    # the median crash by player count
    player_counts = list({g.player_count for g in games})
    crashes = [stat.median(g.crash for g in games if g.player_count == count)/P
               for count in player_counts]

    ax.set_xlabel('player count')
    ax.set_ylabel('median crash')
    ax.bar(player_counts, crashes)


def plot_player_count_by_timestmap(ax, games: Sequence[Game]):
    # player count by timestmap
    games_by_timestamp = sorted(games, key=lambda g: g.timestamp)

    player_counts = [g.player_count for g in games_by_timestamp]

    ax.set_xlabel('date')
    ax.set_ylabel('player count')

    dates = [mdates.datetime.datetime.fromtimestamp(g.timestamp) for g in games_by_timestamp]
    datenums = mdates.date2num(dates)

    ax.plot(datenums, player_counts)

    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%y'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())


def scatter_by(ax, games: Sequence[Game], x: Callable[[Game], Any], y: Callable[[Game], Any],
               *, ptsize=None, xlabel=None, ylabel=None, xscale=None, yscale=None, color=None):
    x_data = tuple(map(x, games))
    y_data = tuple(map(y, games))
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if xscale is not None:
        ax.set_xscale(xscale)
    if yscale is not None:
        ax.set_yscale(yscale)
    ax.scatter(x_data, y_data, s=ptsize, color=color)


def get_cashout_info(cashout: int, games: Sequence[Game]):
    bigger_crash_count = len(games) - bisect(games, cashout, key=lambda g: g.crash) + 1
    return f'On a total of {len(games)} games, {bigger_crash_count} ({bigger_crash_count/len(games)}) crashed >= {cashout/P}.'


if __name__ == '__main__':
    main()

# Highest crash ever : 50041.32 (5962307)

# 128: 8.48: Diff: 3.833% Gain: 35.5%
# 220: 7.52: Diff: 2.157% Gain: 16.218%
# 331: 6.48: Diff: 1.49%  Gain: 7.508%
# 452: 4.45: Diff: 0.758% Gain: 3.374%
# 510: 2.18: Diff: 1.187% Gain: 2.588%
# 604: 2.18: Diff: 1.811% Gain: 3.947%
# 773: 4.81: Diff: 0.685% Gain: 3.294%
# 1377: 8.46: Diff: 0.235% Gain: 1.987%
