import numpy as np
import pandas as pd
import zepid


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
    y_a1 = g_formula.marginal_outcome

    g_formula.fit("none")  # T=0
    y_a0 = g_formula.marginal_outcome

    ATE = np.round(y_a1 - y_a0, 6)
    return ATE


if __name__ == '__main__':
    data = pd.read_csv("/Users/noyantoksoy/Downloads/data_300_with_extra_info_fixed.csv")
    data = format_data(data)

    without_confounders = apply_g_formula(data, "T")
    with_confounders = apply_g_formula(data, "T + L1 + L2 + L3 + L4 + L5 + T:L1 + T:L2 + T:L3 + T:L4 + T:L5")
    print("ATE without the confounder:", without_confounders)
    print("ATE with the confounders:", with_confounders)
    print("Effect of the confounders:", without_confounders - with_confounders)

    # ate_list = []
    # for i in range(1000):
    #     data_ = data.sample(n=data.shape[0], replace=True)
    #     g_formula = zepid.causal.gformula.TimeFixedGFormula(data_, exposure="T", outcome="Y")
    #     g_formula.outcome_model("T + L + T:L ", print_results=False)
    #
    #     g_formula.fit("all")  # T=1
    #     y_a1 = g_formula.marginal_outcome
    #
    #     g_formula.fit("none")  # T=0
    #     y_a0 = g_formula.marginal_outcome
    #
    #     ate_list.append(y_a1 - y_a0)
    #
    # ate_se = np.std(ate_list, ddof=1)
    # print("Normal approx method:", np.round([ATE - 1.96 * ate_se,
    #                                          ATE + 1.96 * ate_se], 6))
