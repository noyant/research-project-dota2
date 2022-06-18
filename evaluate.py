import json

import numpy as np
import pandas as pd
import zepid
import matplotlib.pyplot as plt
from scipy import stats


def helper_game_outcome(team, radiant_win):
    # False -> Radiant, True -> Dire

    # False False -> 0
    # False True -> 1
    # True False -> 1
    # True True -> 0
    return int((bool(team) ^ radiant_win))


def format_data(df):
    df = df.assign(
        team=lambda x: list(
            map(lambda y: 0 if str(y) in ["0", "1", "2", "3", "4"] else 1, list(x["player_slot"].values))))

    df = df.assign(
        Y=lambda x: list(
            map(lambda team, radiant_win: helper_game_outcome(team, radiant_win),
                list(x["team"].values), list(x["radiant_win"].values))))

    df_treatment = df[df.hero_id.apply(lambda x: 14 == x)]
    match_ids = list(df_treatment["match_id"].values)
    teams = list(df_treatment["team"].values)
    df = df.assign(
        T=lambda x: list(
            map(lambda match_id, team: 1 if match_id in match_ids and teams[match_ids.index(match_id)] == team else 0,
                list(x["match_id"].values), list(x["team"].values))))

    df.rename(columns={"pudge_win_rate": "L1"}, inplace=True)
    df.rename(columns={"pudge_kda": "L2"}, inplace=True)
    df.rename(columns={"mmr_estimate": "L3"}, inplace=True)
    df.rename(columns={"counter_performance": "L4"}, inplace=True)
    df.rename(columns={"team_balance": "L5"}, inplace=True)
    df.reset_index()
    df.drop(df.filter(regex='Unnamed').columns, inplace=True, axis=1)
    df.drop("radiant_win", inplace=True, axis=1)
    df.drop("player_slot", inplace=True, axis=1)
    df.drop("picks_bans", inplace=True, axis=1)
    return df


def apply_g_formula(data_, regression_formula):
    g_formula = zepid.causal.gformula.TimeFixedGFormula(data_, exposure="T", outcome="Y")
    g_formula.outcome_model(regression_formula, print_results=False)

    g_formula.fit("all")  # T=1
    E_Y_treatment = g_formula.marginal_outcome

    g_formula.fit("none")  # T=0
    E_Y_no_treatment = g_formula.marginal_outcome

    ATE = np.round(E_Y_treatment - E_Y_no_treatment, 6)
    return ATE


if __name__ == '__main__':
    # data = pd.read_csv("/Users/noyantoksoy/Downloads/data_merged_captains_final.csv")
    # data = format_data(data)
    # data.to_csv("/Users/noyantoksoy/Downloads/data_merged_captains_final_formatted.csv")

    data = pd.read_csv("/Users/noyantoksoy/Downloads/data_merged_captains_final_formatted.csv")
    # data_cop = data.copy()
    #
    # data_cop.rename(columns={"L1": "pudge_win_rate"}, inplace=True)
    # data_cop.rename(columns={"L2": "pudge_kda"}, inplace=True)
    # data_cop.rename(columns={"L3": "mmr_estimate"}, inplace=True)
    # data_cop.rename(columns={"L4": "counter_performance"}, inplace=True)
    # data_cop.rename(columns={"L5": "team_balance"}, inplace=True)
    #
    # data_cop.iloc[:, 6:].describe().to_csv("/Users/noyantoksoy/Downloads/data_merged_captains_final_summary.csv")
    #
    # data_cop.iloc[:, [5]].hist(bins=50)
    # plt.savefig("/Users/noyantoksoy/Downloads/hero_pick_histogram.png")
    # data_cop.iloc[:, [6]].hist(bins=50)
    # plt.savefig("/Users/noyantoksoy/Downloads/pudge_win_rate_histogram.png")
    # data_cop.iloc[:, [7]].hist(bins=50)
    # plt.savefig("/Users/noyantoksoy/Downloads/pudge_kda_histogram.png")
    # data_cop.iloc[:, [8]].hist(bins=50)
    # plt.savefig("/Users/noyantoksoy/Downloads/mmr_estimate_histogram.png")
    # data_cop.iloc[:, [9]].hist(bins=50)
    # plt.savefig("/Users/noyantoksoy/Downloads/counter_performance_histogram.png")
    # data_cop.iloc[:, [10]].hist(bins=25)
    # plt.savefig("/Users/noyantoksoy/Downloads/team_balance_histogram.png")
    # # data_cop.iloc[:, [12]].plot.bar(title="Treatment application")
    # # plt.savefig("/Users/noyantoksoy/Downloads/treatment_histogram.png")
    # plt.show()
    #
    # without_confounders = apply_g_formula(data, "T")
    # with_win_rate = apply_g_formula(data, "T + L1 + T:L1")
    # with_kda = apply_g_formula(data, "T + L2 + T:L2")
    # with_mmr = apply_g_formula(data, "T + L3 + T:L3")
    # with_counter_performance = apply_g_formula(data, "T + L4 + T:L4")
    # with_team_balance = apply_g_formula(data, "T + L5 + T:L5")
    ATE = apply_g_formula(data, "T + L1 + L2 + L3 + L4 + L5 + T:L1 + T:L2 + T:L3 + T:L4 + T:L5")
    # print("ATE without the confounder:", np.round(without_confounders, 6))
    # print("|| ATE with the confounders: ||", np.round(ATE, 6))
    # print("Effect of the confounders:", np.round(ATE - without_confounders, 6))
    # print("--------")
    # print("Effect of Pudge win_rate:", np.round(with_win_rate - without_confounders, 6))
    # print("Effect of Pudge kda:", np.round(with_kda - without_confounders, 6))
    # print("Effect of MMR:", np.round(with_mmr - without_confounders, 6))
    # print("Effect of counter-pick performance:", np.round(with_counter_performance - without_confounders, 6))
    # print("Effect of team balance:", np.round(with_team_balance - without_confounders, 6))

    # ate_list = list(map(lambda x: apply_g_formula(data.sample(n=data.shape[0], replace=True),
    #                                               "T + L1 + L2 + L3 + L4 + L5 + T:L1 + T:L2 + T:L3 + T:L4 + T:L5"),
    #                     range(2000)))
    # with open("/Users/noyantoksoy/Documents/research-project-dota2/data/bootstrap_ate_result.json", "w") as fp:
    #     json.dump(ate_list, fp)

    with open("/Users/noyantoksoy/Documents/research-project-dota2/data/bootstrap_ate_result.json", 'rb') as fp:
        ate_list: list = json.load(fp)

    ATE_se = np.std(ate_list, ddof=1)
    print("--------")
    confidence_interval = np.round([ATE - 1.96 * ATE_se, ATE + 1.96 * ATE_se], 6)
    print("95% confidence interval:", confidence_interval)
    print("Mean of the ATEs, bootstrapping:", np.round(np.mean(ate_list), 6))
    mu, std = stats.norm.fit(ate_list)
    plt.hist(ate_list, density=True, bins=30)
    x_min, x_max = plt.xlim()
    x = np.linspace(x_min, x_max, 100)
    y = stats.norm.pdf(x, mu, std)
    plt.plot(x, y, "k", linewidth=2)
    plt.vlines((confidence_interval[0], confidence_interval[1]), ymin=0, ymax=10, colors=("g", "g"))
    plt.title("95% Confidence interval for the ATE")
    plt.savefig("/Users/noyantoksoy/Downloads/confidence_interval_histogram.png")
    plt.show()

