#!/usr/bin/env python3

from time import sleep
from random import random
from math import floor, ceil, e
from random import SystemRandom

SYSRAND=SystemRandom()

def test(proba: float) -> bool:
    #return random() < proba
    return SYSRAND.random() < proba

CASHOUT = 760.38
PROBA = .0013982300884955753

SEUIL_CRITIQUE = floor(32 / PROBA)

total_spent = 0
total_gains = 0

balance = floor(2 * e / PROBA)

gains = 0
game_count = 0

print("Seuil critique:", SEUIL_CRITIQUE)
print("Balance début:", balance)
input()

try:
    while balance > 0:
        game_count += 1

        bet = max(1, floor(balance / SEUIL_CRITIQUE))
        #mise = 1
        print(f'game {game_count}, bal {balance}, bet {bet}: ', end = '')

        total_spent += bet
        balance -= bet

        if test(PROBA):
            gain = floor(bet * CASHOUT)
            total_gains += gain
            balance += gain
            gains += 1
            #print(f'won {gain-mise}', end = '')
            #input()
        else:
            #print('lost')
            pass
        print(end='\r')

except KeyboardInterrupt:
    pass

print(f"\nBilan après {game_count} parties:")
print(f"{game_count - gains} pertes, {gains} gains")
print(f"{total_spent} Ethos dépensés, {total_gains} gagnés")
print(f"Total: {total_gains-total_spent} ({'perdant' if total_gains < total_spent else 'gagnant'})")
