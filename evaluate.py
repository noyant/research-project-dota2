import numpy as np
import pandas as pd
import zepid


def format_data(df):
    df["T"] = 0
    df["Y"] = 0
    df["team"] = 0  # 0 -> radiant, 1-> dire
    df_radiant = df.copy()
    df_dire = df.copy()

    df_radiant.loc[df_radiant[df_radiant["radiant_win"] == True].index, "Y"] = 1
    df_radiant.rename(columns={"radiant_team": "heroes"}, inplace=True)
    radiant_mask = df_radiant.heroes.apply(lambda x: "14" in x.split(","))
    df_radiant.loc[df_radiant[radiant_mask].index, "T"] = 1

    df_dire.loc[df_dire[df_dire["radiant_win"] == False].index, "Y"] = 1
    df_dire.rename(columns={"dire_team": "heroes"}, inplace=True)
    dire_mask = df_dire.heroes.apply(lambda x: "14" in x.split(","))
    df_dire.loc[df_dire[dire_mask].index, "T"] = 1
    df_dire["team"] = 1

    df = pd.concat([df_radiant, df_dire], ignore_index=True)
    df.rename(columns={"avg_mmr": "L"}, inplace=True)
    df.reset_index()
    df.drop("Unnamed: 0", inplace=True, axis=1)
    df.drop("dire_team", inplace=True, axis=1)
    df.drop("radiant_team", inplace=True, axis=1)
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
    data = pd.read_csv("/Users/noyantoksoy/Downloads/data_merged_new.csv")
    data = format_data(data)

    without_confounder = apply_g_formula(data, "T")
    with_confounder = apply_g_formula(data, "T + L + T:L")
    print("ATE without the confounder:", without_confounder)
    print("ATE with the confounder:", with_confounder)
    print("Effect of the confounder:", without_confounder - with_confounder)

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
