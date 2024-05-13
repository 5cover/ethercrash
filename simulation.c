//usr/bin/gcc -Wall -Wextra -pedantic -fanalyzer -O2 "$0" -lm; if [ $? -eq 0 ]; then ./a.out "$@"; rm ./a.out; fi; exit

#include <stdint.h>
#include <math.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/random.h>

typedef long double Float;
typedef long Int;

#define CASHOUT 760.38
#define PROBA 0.0013982300884955753
#define SEUIL_CRITIQUE ((Int)floorl(12 / PROBA))

bool test(void);
void print_conclusion(void);

bool test(void)
{
    uintmax_t seed;
    if (getrandom(&seed, sizeof seed, 0) < (ssize_t)sizeof seed) {
        perror("getrandom");
        return EXIT_FAILURE;
    }
    return seed / (Float)UINTMAX_MAX < PROBA;
}

static struct {
    Int total_spent;
    Int total_gains;
    Int balance;
    Int gains;
    Int game_count;
} gs_state;

int main()
{
    atexit(print_conclusion);

    gs_state.total_spent = 0;
    gs_state.total_gains = 0;

    gs_state.balance = (Int)floorl(15 / PROBA);

    gs_state.gains = 0;
    gs_state.game_count = 0;

    printf("seul critique: %ld, ", SEUIL_CRITIQUE);
    printf("balance début: %ld ", gs_state.balance);

    while (gs_state.balance > 0 && gs_state.game_count < 100000) {
        ++gs_state.game_count;

        Int bet = (Int)floorl(gs_state.balance / SEUIL_CRITIQUE);
        if (bet < 1) bet = 1;
        //Int bet = 1;

        //printf("game %ld, bal %ld, bet %ld: ", gs_state.game_count, gs_state.balance, bet);

        gs_state.total_spent += bet;
        gs_state.balance -= bet;

        if (test()) {
            Int gain = (Int)floorl(bet * CASHOUT);
            gs_state.total_gains += gain;
            gs_state.balance += gain;
            ++gs_state.gains;
            //getchar();
        }
        //putchar('\r');
    }
}

void print_conclusion() {
    //printf("Bilan après %ld parties:\n", gs_state.game_count);
    //printf("%ld pertes, %ld gains (%.3Lf%%)\n", gs_state.game_count - gs_state.gains, gs_state.gains, gs_state.gains * 100 / (Float)gs_state.game_count);
    //printf("%ld Ethos dépensés, %ld gagnés\n", gs_state.total_spent, gs_state.total_gains);
    Int result = gs_state.total_gains - gs_state.total_spent;
    printf("Total: %ld (%s)", result, result < 0 ? "perdu" : "GAGNE");
}