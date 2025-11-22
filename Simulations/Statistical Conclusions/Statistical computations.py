import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

csv = pd.read_csv("Simulations/Results/simulation_results2.csv")
strategies = ['Greedy', 'MCTS', 'Minimax', 'Random', 'SafeChoice']


    ### Win rate per strategy
print("\n\033[1m      Win Rate per Strategy \033[0m")

rows = []
for s in strategies:
    s1 = csv[csv["S1"] == s]
    s2 = csv[csv["S2"] == s]

    wins = (
        s1["S1_wins_as_P1"].sum()
        + s1["S1_wins_as_P2"].sum()
        + s2["S2_wins_as_P1"].sum()
        + s2["S2_wins_as_P2"].sum() )
    losses = (
        s1["S2_wins_as_P1"].sum()
        + s1["S2_wins_as_P2"].sum()
        + s2["S1_wins_as_P1"].sum()
        + s2["S1_wins_as_P2"].sum() )
    n = wins + losses
    rows.append({"strategy": s, "wins": wins, "losses": losses, "win_rate": wins / n if n else None})

results = pd.DataFrame(rows).sort_values("win_rate", ascending=False)
print(results)


    ### Win rate of each strategy against another
print("\n\033[1m      Win rate of each strategy against another \033[0m")

# Use both S1 and S2 roles so we count both orientations
s1_part = csv[["S1", "S2", "S1_overall_win_rate"]].rename(
    columns={"S1": "A", "S2": "B", "S1_overall_win_rate": "A_win_rate"} )
s2_part = csv[["S2", "S1", "S2_overall_win_rate"]].rename(
    columns={"S2": "A", "S1": "B", "S2_overall_win_rate": "A_win_rate"} )

# Concatenate the strategies and relatives win rate
both = pd.concat([s1_part, s2_part], ignore_index=True)

# Average A’s win rates over all matches vs B, regroup all the datas
h2h = both.groupby(["A", "B"], as_index=False)["A_win_rate"].mean()

# Shapes the table
matrix = h2h.pivot(index="A", columns="B", values="A_win_rate").sort_index(axis=0).sort_index(axis=1)

print(matrix.round(3))

#Plot the heatmap of each strategy performance against the others

plt.figure(figsize=(8,6))
sns.heatmap(matrix, annot=True, cmap="coolwarm", vmin=0, vmax=1)
plt.title("Strategy vs Strategy Win Rates")
plt.xlabel("Opponent")
plt.ylabel("Strategy")
#plt.show()

    ###Win rates of Strategies relatively to board size
print("\n\033[1m      Win rates of Strategies relatively to board size \033[0m")

records = []
board_size= [3,5,6,8,9]
for s in strategies:
    for size in board_size:

        s1 = csv[(csv["S1"] == s) & (csv["board_size"] == size)]
        s2 = csv[(csv["S2"] == s) & (csv["board_size"] == size)]

        wins = (
            s1["S1_wins_as_P1"].sum() + s1["S1_wins_as_P2"].sum() +
            s2["S2_wins_as_P1"].sum() + s2["S2_wins_as_P2"].sum() )
        losses = (
            s1["S2_wins_as_P1"].sum() + s1["S2_wins_as_P2"].sum() +
            s2["S1_wins_as_P1"].sum() + s2["S1_wins_as_P2"].sum() )

        total = wins + losses
        win_rate = wins / total if total > 0 else None
        records.append({"strategy": s, "board_size": size, "win_rate": win_rate})

win_rates = pd.DataFrame(records)
print(win_rates)

# Win rate: mean, standard deviation, coefficient of variation for each strategy
print("\n\033[1m      Consistency of strategies against board size \033[0m")

consistency = (
    win_rates.groupby("strategy")["win_rate"]
    .agg(["mean", "std"])
    .reset_index() )
consistency["cv"] = consistency["std"] / consistency["mean"]

print(consistency)


    ###PLOT Win Rate per Strategy across Board Sizes

plt.figure(figsize=(8,5))
sns.lineplot(data=win_rates, x="board_size", y="win_rate", hue="strategy", marker="o")
plt.title("Win Rate per Strategy across Board Sizes")
plt.xlabel("Board Size")
plt.ylabel("Win Rate")
plt.ylim(0, 1)
plt.legend(title="Strategy")
#plt.show()


    ### Tie rate
print("\n\033[1m      Tie rate \033[0m")
rows = []
for s in strategies:
    s1 = csv[csv["S1"] == s]
    s2 = csv[csv["S2"] == s]
    ties = int(s1["ties"].sum() + s2["ties"].sum())
    total_games = int(s1["total_games_matchup"].sum() + s2["total_games_matchup"].sum())
    tie_rate = ties / total_games if total_games > 0 else float("nan")
    rows.append({"strategy": s, "ties": ties, "total_games": total_games, "tie_rate": tie_rate})

tie = pd.DataFrame(rows).sort_values("tie_rate", ascending=False)
print(tie)
###Interesting thing, with boards greater than 2x2 when there is the random strategy involved there is NEVER a tie


    ###First move advantage
print("\n\033[1m      First move advantage \033[0m")
# Compute starter advantage per strategy and board size
records = []
for s in strategies:
    for size in board_size:
        subset = csv[((csv["S1"] == s) | (csv["S2"] == s)) & (csv["board_size"] == size)]
        total_games = subset["total_games_matchup"].sum()
        starter_win_rate = np.average(subset["starter_win_rate"], weights=subset["total_games_matchup"])
        starter_wins = starter_win_rate * total_games
        records.append({
            "strategy": s,
            "board_size": size,
            "starter_win_rate": starter_win_rate,
            "total_games": total_games
        })

first_move_by_strategy_size = pd.DataFrame(records)

# Sort and display results
first_move_by_strategy_size = first_move_by_strategy_size.sort_values(["strategy", "board_size"]).reset_index(drop=True)
print(first_move_by_strategy_size)


###PLOT first move adv

plt.figure(figsize=(8,5))
sns.lineplot(
    data=first_move_by_strategy_size,
    x="board_size",
    y="starter_win_rate",
    hue="strategy",
    marker="o" )
plt.title("First-Move Advantage per Strategy across Board Sizes")
plt.xlabel("Board Size")
plt.ylabel("Starter Win Rate")
plt.ylim(0, 1)
plt.legend(title="Strategy")
plt.tight_layout()
#plt.show()

# Plot heatmap
pivot = first_move_by_strategy_size.pivot(
    index="strategy",
    columns="board_size",
    values="starter_win_rate" )

plt.figure(figsize=(8,5))
sns.heatmap(pivot, annot=True, fmt=".3f", cmap="YlGnBu", vmin=0.5, vmax=0.9)
plt.title("First-Move Advantage Heatmap (Win Rate)")
plt.xlabel("Board Size")
plt.ylabel("Strategy")
plt.tight_layout()
plt.show()