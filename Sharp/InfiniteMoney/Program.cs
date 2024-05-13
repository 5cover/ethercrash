double[] src = { 2.71, 2.03, 1.17, 7.53, 1.22, 13.85, 1.46, 6.98, 1.24, 16.14, 1.09, 4.64, 4.1, 0, 6.49, 1.14, 4.51, 2.68, 45.59,
    1.05, 13.21, 59.16, 3.06, 1.54, 1.31, 1.28, 5.82, 28.97, 2.38, 1.27, 3.03, 3.22, 0, 10.02, 2.77, 1.03, 6.05, 4.06, 1.74, 1.2, 1.02,
    1.19, 1.47, 9.09, 1.22, 1.09, 1.54, 1.63, 1.13, 1.64, 3.97, 1.78, 1.51, 2.41, 8.58, 2.72, 15.24, 2.07, 1.63, 3.31, 1.18, 8.49, 2.98,
    2.52, 15.56, 10.33, 1.03, 1.35, 1.68, 1.23, 2.27, 1.73, 1.12, 5.74, 8.61, 1.04, 1.93, 1.09, 2.45, 1.12, 2.57, 8.57, 373.73, 1.88,
    1.53, 5.96, 1.53, 3.79, 4.46, 1.47, 1.17, 2.56, 3.01, 22.57, 46.83, 2.46, 1, 2.45, 1, 7.71, 4.03, 1.88, 1.06, 1.16, 1.88, 5.78,
    1.81, 1.7, 23.91, 1.68, 4.2, 1.08, 1.37, 1.16, 1.65, 1.94, 5.22, 15.73, 2.66, 1.05, 5.02, 2.28, 1.05, 1.04, 4.82, 1.86, 1.11, 1.33,
    17.3, 1.37, 9.91, 2.11, 9.19, 3.76, 1.05, 1.56, 1.66, 1.6, 1.02, 1.26, 3.66, 4.13, 1.21, 17.64, 1.03, 1.25, 2.15, 1.43, 16.17, 5.53,
    1.14, 1.18, 2.32, 2.07, 2.81, 15.34, 1.04, 1.86, 1.06, 1.71, 2.71, 1.6, 1.67, 4.39, 3.71, 1.25, 1.67, 1.21, 15.76, 1.68, 1.08, 1.29,
    4.97, 2.09, 10.32, 2.19, 7.82, 1.51, 5.49, 8.06, 1.57, 1.13, 2.75, 2.49, 6.66, 2.9, 1.69, 17.4, 1.28, 6.6, 1.01, 2.22, 1.25, 5.23,
    1.88, 1.05, 1.22, 2.69, 3.03, 2.22, 5.6, 1.17, 2.19, 3.01, 1.49, 5.26, 1.27, 1.01, 1.27, 1.71, 2.44, 1.07, 1.35, 2.74, 4.03, 1.11,
    1.26, 15.15, 0, 1.05, 83,77, 3.37, 1.37, 1.57, 4.07, 1.2, 2.58, 2.42, 6.55, 1.06, 4.84, 9.63, 2.85, 1.03, 1.3, 1.13, 1.5, 2.24, 1.85, 1, 49.31, 1.06,
    10.59, 9.68, 6.5, 1.48, 6.29, 2.25, 1.07, 4.26, 3.08, 1.8, 1.16, 1.73, 2.47, 2.19, 1.06, 1.38, 3.19, 4.84, 1.04, 1.66, 1.59, 1.07, 1.32, 3.37, 2.02,
    7.26, 1.64, 2.58, 1.64, 10.84, 1.22, 2.05, 7.6, 1.02, 2.23, 1.39, 1.25, 6.77, 1.56, 2.44, 1.32, 2.97, 1.3, 7.12, 1.23, 3.93, 2.04, 3.05, 1.56, 3.16,
    2.53, 2.38, 10.72, 1.15, 1, 1.12, 2.04, 1.57, 1.12, 2.83, 1.03, 3.04, 11.92, 1.06, 1.46, 2.35, 2.86, 3.08, 12.23, 1.17, 4.89, 4.49, 1.8, 67.93, 1.49,
    1.51, 2.83, 1.11, 4.14, 1.28, 1.18, 1.02, 1.12, 63.18, 1.58, 2.27, 1.58, 1.05, };

IReadOnlyCollection<int> cashAts = src.Select(ca => Convert.ToInt32(ca * 100)).ToList();

const int Min = 100; // 1
const int Max = 1000; // 10

var stats = Range(Min, Max + 1).ToDictionary(cashOut => cashOut / 100M, cashOut =>
{
    decimal actualCashOut = cashOut / 100M;

    // Count of wins with this cashout
    int count = cashAts.Count(ca => ca > cashOut);

    // Minimum win probability for a net neutral
    decimal pMin = 1M / actualCashOut;

    // Actual win probability according to the data
    decimal pActual = (decimal)count / cashAts.Count;

    // Return the difference times the cashout
    (decimal diff, decimal gain) stat = (pActual - pMin, (pActual - pMin) * actualCashOut);
    return stat;

    // En gros c'est la différence entre la probabilité de gagner et la probabilité minimale pour rentrer
    // dans ses frais
    // Le gain c'est la différence multipliée par le risque pris
});

foreach (var stat in stats.OrderBy(kv => kv.Value.gain))
{
    Console.WriteLine($"{stat.Key}: Diff: {stat.Value.diff:p} Gain: {stat.Value.gain:p}");
}

Console.WriteLine($"Length: {cashAts.Count}");

// -128 : Best cashout: 4.0 (diff: ~5%)
// -220 : best cashout : 3.96 (diff: 3.38%)
// -331 : best cashout : 4.02 (diff: 1.71%)
// -331 : best cashout : 6.48 (diff: 1,49%, gain: 9.63%)

// Idea : multiply difference by cashout -> more risks, more reward

static IEnumerable<int> Range(int start, int stop, int step = 1)
{
    if (step == 0)
    {
        throw new ArgumentException("Step cannot be zero.");
    }

    if (step > 0 && start >= stop)
    {
        yield break;
    }
    else if (step < 0 && start <= stop)
    {
        yield break;
    }

    for (int i = start; step > 0 ? i < stop : i > stop; i += step)
    {
        yield return i;
    }
}