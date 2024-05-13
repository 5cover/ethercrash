# Project status

8/05/2024 : i want to retry this. No more gain. Focus on safety and minimal losses. understand your own code. go back to the website

Get some more recent crashes

It doesn't matter how much we bet, but when do we cashout.

If we cashout early, we will win more often but we will get less, probably not enough to cover our losses.

If we cashout too late, we will win rarely but we will earn a lot, but again, maybe to rarely to cover our losses.

Where is the middle ground ?

Other things that we could do : try and see if there are patterns that result in higher crashes, related to id and date maybe

store the start date in unix seconds.

also we could get the sum of bets, maybe it affects the cashout.

## stats i'd like to get

- evolution of bet sum over time : did people use to bet more/less?
- proportionality of bet/crash : are people able to predict it?
- distribution of cashout values - is it exponential?

## combien miser

l'objectif c'est de jamais tomber à court car on ne gagne pas assez souvent.

Mais en même temps il faudrait miser le plus possible pour gagner plus.

Parce qu'en misant 1 tout le temps on ne gagne que très peu.

Combien est-ce qu'on peut miser au maximum, prenant en compte le gain

Le gain à 760.38 est de 6.746%. Donc si on mise 100, $100*(1+0.06746) = 106.746$.

Mais on s'en fiche. Car il faut prendre en compte la possibilité de perte.

La probabilité de 760.38 est 0.13982300884955753%.

La probabilité de perdre est 99.860176991%.

En moyenne, on gagnera une fois toutes les 715.189873418 parties.

L'idée, c'est de jamais tout perdre. Donc, il ne faut jamais miser plus que ce qu'on pourrait perdre d'ici au prochain gain.

Donc il faudrait toujours avoir au moins 716 pour pouvoir gagner en misant 1.

On va appeler ça le **seuil critique**. En pratique, on le multipliera par une constante ($\phi$?) pour s'assurer d'avoir toujours assez même en cas de malchance.

$$\text{proba} = 0.0013982300884955753$$

$$\text{seuil critique}=\frac{218}{\text{proba}}$$

Si notre balance est au-dessus du seuil critique, on peut se permettre de miser plus. Mais combien exactement?

$$\text{mise} = max(1, floor(\frac{\text{balance}}{\text{seuil critique}}))$$

Ok.. I give up.. positive gain cashouts are too high and surely caused by statistical errors.

BUT there is still hope. Predicting crash values.

## Predicting crash values

Scatter:

y|x
Crash value|total bet
Crash value|timestamp
Crash value|player count

maybe we can identify patterns in the data but we need to scrape MORE.

start > done + current - remaining > end

start > (start - remaining | done + end) > end

I need more data. Any pattern i can observe now is likely due to a statistical error.

Maybe we can find a pattern for the 0 crash.
