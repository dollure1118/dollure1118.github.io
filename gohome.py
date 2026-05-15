# # 6.6.9.

# import pandas as pd
# import polars as pl
# import numpy as np
# import pybabynames as bn 

# babynames = pd.read_csv("data/babynames.csv")
# lifetables = bn.lifetables.to_pandas()

# # 문제: 각 이름을 가진 사람들이 2014년에 몇 명 정도 살아 있을지 추정한 열을 기존 DataFrame에 추가하는 것

# # 1. lifetables 자료 정리
# actuarial = (
#     lifetables
#     .assign(
#         age_today=lambda df: df["x"],
#         alive_prob=lambda df: df["lx"] / 100000,   # lx = 10만 명 기준 x세까지 산 사람 수
#         more_years=lambda df: df["ex"],            # ex = 앞으로 더 살 것으로 기대되는 평균 연수
#         life_exp=lambda df: df["x"] + df["ex"]     # 총 기대수명
#     )
# )

# actuarial = (
#     actuarial[actuarial["year"] + actuarial["x"] == 2014]
#     [["year", "sex", "age_today", "alive_prob", "life_exp"]]
# )

# # 2. 연도 범위 만들기
# years = np.arange(actuarial["year"].min(), actuarial["year"].max() + 1)

# # 생존확률 자료가 모든 출생연도별로 있지 않고 10년 단위로 존재한다.
# # 따라서 이를 연속으로 만들기 위해 선형보간 함수를 사용한다.
# def approximate(data, years):
#     data = data.sort_values("year")

#     return pd.DataFrame({
#         "year": years,
#         "alive_prob": np.interp(
#             x=years,                       # 새로 계산하고 싶은 연도
#             xp=data["year"],               # 보간의 기준점
#             fp=data["alive_prob"]          # 보간할 생존확률
#         )
#     })


# # lifetables 데이터에는 sex 열이 따로 있다.
# # 성별에 따라 생존율이 다르므로 남녀를 나누어 계산한다.
# men = approximate(
#     actuarial[actuarial["sex"] == "M"],
#     years
# )
# men["sex"] = "M"

# women = approximate(
#     actuarial[actuarial["sex"] == "F"],
#     years
# )
# women["sex"] = "F"

# # 4. 보간 결과 합치기
# actuarial_interp = pd.concat([men, women], ignore_index=True)

# # 5. babynames 자료와 결합
# BabynamesDist = (
#     babynames
#     .merge(actuarial_interp, on=["year", "sex"], how="inner")
#     .assign(
#         count_thousands=lambda df: df["n"] / 1000,
#         age_today=lambda df: 2014 - df["year"],
#         est_alive_today=lambda df: df["n"] * df["alive_prob"]  # 2014년에도 살아있을 추정 인원
#     )
# )
# pd.set_option("display.max_rows", None)
# print(BabynamesDist.head())

# # 6.6.10.

# import pandas as pd
# from plotnine import ggplot, aes, geom_line, facet_wrap, labs

# Teams=pd.read_csv("data/Teams.csv")
# # Teams DataFrame이 이미 준비되어 있다고 가정

# cubs_hr = (
#     Teams
#     .query("teamID == 'CHN'")
#     [["yearID", "HR", "HRA"]]
#     .melt(
#         id_vars="yearID",
#         value_vars=["HR", "HRA"],      # HRA: 허용한 홈런 수
#         var_name="type",               # HR과 HRA를 같은 변수 구조 안에서 비교할 수 있게 만든다
#         value_name="home_runs"
#     )
# )

# cubs_hr.head()

# p=(
#     ggplot(cubs_hr, aes(x="yearID", y="home_runs"))
#     + geom_line()
#     + facet_wrap("~ type")             # 타입별 그래프 분류
#     + labs(
#         title="CHN Home Runs: HR vs HR Allowed",
#         x="Year",
#         y="Number of Home Runs"
#     )
# )

# p.show()


# # 7.9.5.
# import pandas as pd
# import matplotlib.pyplot as plt
# from plotnine import (
#     ggplot, aes, geom_jitter, geom_smooth,
#     geom_boxplot, labs
# )

# NHANES=pd.read_csv("data/NHANES.csv")
# # NHANES DataFrame이 이미 준비되어 있다고 가정

# def pulse_plot(data, x_var):
    
#     plot_data = (
#         data[["Pulse", x_var]]
#         .dropna()                         # Pulse 또는 x축 변수에 결측치가 있는 행 제거
#     )
    
#     return (
#         ggplot(plot_data, aes(x=x_var, y="Pulse"))
#         + geom_jitter(alpha=0.3)           # 점들이 겹치지 않게 약간 흩뿌려 산점도를 그림
#         + geom_smooth(se=False)            # Pulse와 x축 변수 사이의 전반적 추세선을 그림
#         + labs(
#             title=f"Pulse by {x_var}",
#             subtitle="source = NHANES",
#             x=x_var,
#             y="Pulse"
#         )
#     )


# pulse_vars = ["Age", "BMI", "BPSysAve"]    # Pulse와 비교할 변수들

# pulse_plots = [
#     pulse_plot(NHANES, x_var)
#     for x_var in pulse_vars
# ]

# for p in pulse_plots[:2]:
#     fig = p.draw()
#     plt.show()

# # Pulse는 Age, BMI, BPSysAve와 강한 선형관계를 보이지 않는다.
# # 얼추 직선을 띠는 변수들도 있으나 그 산포도가 너무 커 신뢰도가 낮다.


# # 변수 중 TVHrsDay는 0_hours..처럼 범주형 변수로 분류된다.
# # 따라서 각 변수마다 상자그림을 통해 분포를 알아본다.
# tv_plot_data = (
#     NHANES[["Pulse", "TVHrsDay"]]
#     .dropna()
# )

# p=(
#     ggplot(tv_plot_data, aes(x="TVHrsDay", y="Pulse"))
#     + geom_boxplot()
#     + geom_jitter(alpha=0.2, width=0.2)     # 점이 지나치게 겹쳐보이지 않게 산포
#     + labs(
#         title="Pulse by TVHrsDay",
#         subtitle="NHANES",
#         x="TV hours per day",
#         y="Pulse"
#     )
# )

# p.show()
# # TVHrsDay도 마찬가지로 강한 상관관계를 띠지는 않는다.


# # 7.9.6.

# import numpy as np
# import pandas as pd
# import plotly.graph_objects as go
# from IPython.display import HTML
# import pylahman

# # Teams, Batting, People DataFrame이 이미 준비되어 있다고 가정
# Teams=pylahman.Teams()
# Batting=pylahman.Batting()
# People=pylahman.People()
# # 시즌별 홈런 수에 대해 그래프를 그려보고자 한다
# team_names = (
#     Teams[["yearID", "lgID", "teamID", "name"]]
#     .rename(columns={"name": "team_name"})
# )

# season_hr = (
#     Batting
#     .merge(team_names, on=["yearID", "lgID", "teamID"], how="left")
# )

# season_hr["team_label"] = season_hr["team_name"].fillna(season_hr["teamID"])

# season_hr = (
#     season_hr
#     .groupby(["playerID", "yearID"], as_index=False)
#     .agg(
#         HR=("HR", lambda x: x.fillna(0).sum()),
#         teams=("team_label", lambda x: ", ".join(pd.Series(x).dropna().unique()))
#     )
# )

# season_hr = season_hr[
#     (season_hr["yearID"] >= 1901) &
#     (season_hr["yearID"] <= 2014)
# ]


# player_names = People.copy()

# player_names["player"] = (
#     player_names["nameFirst"].fillna("") + " " +
#     player_names["nameLast"].fillna("")
# ).str.strip().str.replace(r"\s+", " ", regex=True)

# player_names = player_names[["playerID", "player"]]


# season_hr_named = (
#     season_hr
#     .merge(player_names, on="playerID", how="left")
# )


# # 붉은색 점 선수들 표시
# record_points = (
#     season_hr_named
#     .loc[
#         season_hr_named.groupby("yearID")["HR"].transform("max")
#         == season_hr_named["HR"]
#     ]
#     .copy()
# )

# record_points = (
#     record_points
#     .groupby(["yearID", "HR"], as_index=False)
#     .agg(
#         record_players=("player", lambda x: list(x)),
#         n_record_players=("player", "size"),
#         teams_label=("teams", lambda x: ", ".join(pd.Series(x).dropna().unique()))
#     )
#     .sort_values("yearID")
# )

# record_points["HR"] = record_points["HR"].astype(float)
# record_points["prev_record"] = record_points["HR"].cummax().shift(1).fillna(-np.inf)

# record_points = record_points[
#     record_points["HR"] > record_points["prev_record"]
# ].copy()

# record_points["next_record_year"] = record_points["yearID"].shift(-1)
# record_points["record_stood"] = (
#     record_points["next_record_year"] - record_points["yearID"]
# )
# record_points["xend"] = record_points["next_record_year"].fillna(2014)


# def make_record_tooltip(row):
#     players = "<br>".join(row["record_players"])
    
#     if pd.isna(row["record_stood"]):
#         stood_text = "Current Record"
#     else:
#         stood_text = f"Record stood {int(row['record_stood'])} years"
    
#     return (
#         f"<b>{int(row['HR'])}</b>"
#         f"<br>"
#         f"<b>{players}</b>"
#         f"<br>"
#         f"<span style='font-size:10px'>{int(row['yearID'])}  {row['teams_label']}</span>"
#         f"<br>"
#         f"{stood_text}"
#     )


# record_points["record_tooltip"] = record_points.apply(
#     make_record_tooltip,
#     axis=1
# )


# season_hr_top30 = (
#     season_hr_named
#     .sort_values(["yearID", "HR", "player"], ascending=[True, False, True])
#     .copy()
# )

# season_hr_top30["rank_in_year"] = (
#     season_hr_top30
#     .groupby("yearID")
#     .cumcount() + 1
# )

# season_hr_top30 = season_hr_top30[
#     season_hr_top30["rank_in_year"] <= 30
# ].copy()


# def make_player_team_text(row):
#     return (
#         f"{row['player']}"
#         f"<br>"
#         f"<span style='font-size:10px'>{int(row['yearID'])} {row['teams']}</span>"
#     )


# season_hr_top30["player_team_text"] = season_hr_top30.apply(
#     make_player_team_text,
#     axis=1
# )


# season_hr_grouped = (
#     season_hr_top30
#     .groupby(["yearID", "HR"], as_index=False)
#     .agg(
#         player_team_list=("player_team_text", lambda x: list(x)),
#         n_players=("player_team_text", "size")
#     )
# )


# def make_tooltip(row):
#     if row["n_players"] >= 4:
#         return (
#             f"<b>{int(row['HR'])}</b>"
#             f"<br>"
#             f"{row['n_players']} players"
#         )
#     else:
#         return (
#             f"<b>{int(row['HR'])}</b>"
#             f"<br>"
#             f"{'<br>'.join(row['player_team_list'])}"
#         )


# season_hr_grouped["tooltip"] = season_hr_grouped.apply(
#     make_tooltip,
#     axis=1
# )


# # 이제 설정한 점들을 그려보자
# fig = go.Figure()

# # trace0: 회색 점
# fig.add_trace(
#     go.Scatter(
#         x=season_hr_grouped["yearID"],
#         y=season_hr_grouped["HR"],
#         mode="markers",
#         text=season_hr_grouped["tooltip"],
#         hoverinfo="text",
#         marker=dict(
#             color="rgba(170,170,170,0.55)",
#             size=6
#         ),
#         showlegend=False
#     )
# )

# # trace1: 붉은 점
# fig.add_trace(
#     go.Scatter(
#         x=record_points["yearID"],
#         y=record_points["HR"],
#         mode="markers",
#         text=record_points["record_tooltip"],
#         hoverinfo="text",
#         marker=dict(
#             color="firebrick",
#             size=6
#         ),
#         showlegend=False
#     )
# )

# # trace2, 3, ... : 각 기록 갱신점마다 하나의 수평선
# for _, row in record_points.iterrows():
#     fig.add_trace(
#         go.Scatter(
#             x=[row["yearID"], row["xend"]],
#             y=[row["HR"], row["HR"]],
#             mode="lines",
#             line=dict(
#                 color="firebrick",
#                 width=2
#             ),
#             hoverinfo="skip",
#             visible=False,
#             showlegend=False
#         )
#     )

# line_start_index = 2
# line_indices = list(
#     range(
#         line_start_index,
#         line_start_index + len(record_points)
#     )
# )

# fig.update_layout(
#     title='Home Runs <span style="color:firebrick"><b>49 Years</b></span>',
#     xaxis=dict(
#         title="Year",
#         tick0=1910,
#         dtick=20,
#         range=[1901, 2014]
#     ),
#     yaxis=dict(
#         title="Home Runs"
#     ),
#     annotations=[
#         dict(
#             x=2001,
#             y=73,
#             text="Barry Bonds, 2001 <b>73</b>",
#             showarrow=False,
#             xanchor="left",
#             yanchor="bottom",
#             xshift=10,
#             yshift=8,
#             font=dict(size=14)
#         )
#     ]
# )


# # R의 htmlwidgets::onRender()에 해당하는 JavaScript 후처리
# # 붉은 점에 커서를 올릴 때만 해당 기록 유지선을 보이게 한다.
# post_script = f"""
# var gd = document.getElementById('{{plot_id}}');
# var lineIndices = {line_indices};

# gd.on('plotly_hover', function(eventData) {{
#     var pt = eventData.points[0];

#     Plotly.restyle(gd, {{visible: false}}, lineIndices);

#     if (pt.curveNumber === 1) {{
#         var lineIndex = {line_start_index} + pt.pointNumber;
#         Plotly.restyle(gd, {{visible: true}}, [lineIndex]);
#     }}
# }});

# gd.on('plotly_unhover', function(eventData) {{
#     Plotly.restyle(gd, {{visible: false}}, lineIndices);
# }});
# """

# HTML(
#     fig.to_html(
#         include_plotlyjs="cdn",
#         full_html=False,
#         post_script=post_script
#     )
# )

# 7.7절 확장
# import math
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# from statsmodels.nonparametric.smoothers_lowess import lowess

# NHANES = pd.read_csv("data/NHANES.csv")


# def bmi_plot(ax, data, x_var):
    
#     d = (
#         data[["BMI", x_var]]
#         .dropna(subset=["BMI", x_var])             # BMI 또는 x축 변수에 결측치가 있는 행 제거
#     )
    
#     # 자료가 없으면 빈 그래프 처리
#     if d.empty:
#         ax.axis("off")
#         ax.set_title(f"BMI by {x_var}\nNo data", fontsize=10)
#         return
    
#     x = d[x_var]
#     y = d["BMI"]
    
   
#     # x가 수치형이고, x값 종류가 10개 이상일 때만 산점도 + LOWESS 추세선 사용
#     if pd.api.types.is_numeric_dtype(x) and x.nunique() >= 10:
        
#         ax.scatter(
#             x,
#             y,
#             alpha=0.3,
#             s=10
#         )
        
#         smooth = lowess(
#             endog=y,
#             exog=x,
#             frac=0.3,
#             return_sorted=True
#         )
        
#         ax.plot(
#             smooth[:, 0],
#             smooth[:, 1],
#             "r",
#             linewidth=2
#         )
        
#         ax.set_xlabel(x_var, fontsize=8)
#         ax.set_ylabel("BMI", fontsize=8)
    
#     else:
#         # x가 범주형이거나, 수치형이어도 x값 종류가 10개 미만이면 boxplot 사용
        
#         grouped = list(d.groupby(x_var, sort=True, observed=False))
        
#         groups = [
#             group["BMI"].dropna().values
#             for _, group in grouped
#         ]
        
#         labels = [
#             str(label)
#             for label, _ in grouped
#         ]
        
#         positions = np.arange(1, len(groups) + 1)
        
#         ax.boxplot(
#             groups,
#             positions=positions
#         )
        
#         # geom_jitter(alpha = 0.01, width = 0)에 해당
#         for pos, group in zip(positions, groups):
#             ax.scatter(
#                 np.repeat(pos, len(group)),
#                 group,
#                 alpha=0.01,
#                 s=10
#             )
        
#         ax.set_xticks(positions)
#         ax.set_xticklabels(
#             labels,
#             rotation=45,
#             ha="right",
#             fontsize=7
#         )
        
#         ax.set_xlabel(x_var, fontsize=8)
#         ax.set_ylabel("BMI", fontsize=8)
    
#     ax.set_title(f"BMI by {x_var}\nNHANES", fontsize=10)
#     ax.tick_params(axis="both", labelsize=7)


# # 1. columns를 사용하여 모든 변수와 BMI 비교
# all_vars = [
#     col for col in NHANES.columns
#     if col != "BMI"
# ]

# vars_per_page = 9

# all_vars_pages = [
#     all_vars[i:i + vars_per_page]
#     for i in range(0, len(all_vars), vars_per_page)
# ]


# for page_num, vars_page in enumerate(all_vars_pages, start=1):
    
#     n_plots = len(vars_page)
#     ncol = 3
#     nrow = math.ceil(n_plots / ncol)
    
#     fig, axes = plt.subplots(
#         nrow,
#         ncol,
#         figsize=(12, 4 * nrow)
#     )
    
#     axes = np.array(axes).reshape(-1)
    
#     for ax, x_var in zip(axes, vars_page):
#         bmi_plot(ax, NHANES, x_var)
    
#     # 남는 빈 칸 제거
#     for ax in axes[n_plots:]:
#         ax.axis("off")
    
#     fig.suptitle(
#         f"BMI by NHANES Variables - Page {page_num}",
#         fontsize=14
#     )
    
#     fig.text(
#         0.5,
#         0.01,
#         "Source: US National Center for Health Statistics (NCHS)",
#         ha="center",
#         fontsize=9
#     )
    
#     plt.tight_layout(rect=[0, 0.03, 1, 0.95])
#     plt.show()

# 8.12.10.

# import numpy as np
# import pandas as pd
# from scipy.stats import f
# import statsmodels.formula.api as smf
# from plotnine import ggplot, aes, geom_histogram, labs

# np.random.seed(123)


# def simulate_once(n=250, p=100, alpha=0.05):
    
#     X = np.random.normal(size=(n, p))          # 정규분포를 따르는 난수 n*p 생성, n행 p열의 설명변수 행렬
#     colnames = [f"x{i}" for i in range(1, p + 1)]   # x1, x2, ..., xp 형태의 변수명 생성
    
#     data = pd.DataFrame(X, columns=colnames)
#     data["y"] = np.random.normal(size=n)      # 반응변수 y도 정규분포 난수로 생성
    
#     # x1부터 xp까지 각각 단순회귀를 돌려 p-value를 구한다
#     p_values = []
    
#     for var in colnames:
#         fit = smf.ols(f"y ~ {var}", data=data).fit()
#         p_values.append(fit.pvalues[var])     # t검정 p-value 추출
    
#     p_values = np.array(p_values)
    
#     selected_vars = np.array(colnames)[p_values < alpha]   # p-value가 alpha보다 작은 변수만 선택
    
#     # 선택된 변수들을 모두 넣어 다중선형회귀 적합
#     # ex: y ~ x3 + x17 + ...
#     if len(selected_vars) > 0:
#         formula = "y ~ " + " + ".join(selected_vars)
#         final_fit = smf.ols(formula, data=data).fit()
#         overall_p_value = final_fit.f_pvalue  # 최종모형의 전체 F검정 p-value
#     else:
#         # 선택된 변수가 없으면 절편만 있는 모형이므로 전체 F검정 p-value가 정의되지 않음
#         overall_p_value = np.nan
    
#     return pd.DataFrame({
#         "num_selected": [len(selected_vars)],
#         "overall_p_value": [overall_p_value]
#     })


# sim_result = pd.concat(
#     [simulate_once() for _ in range(100)],
#     ignore_index=True
# )
# # simulate_once()를 1000번 반복 실행하고 결과를 행 방향으로 합친다


# p1=(
#     ggplot(sim_result, aes(x="overall_p_value"))
#     + geom_histogram(binwidth=0.01, boundary=0)
#     + labs(
#         title="Distribution of Overall p-values After Variable Screening",
#         subtitle="Null case: no predictors are truly associated with the outcome",
#         x="Overall model p-value",
#         y="Count",
#         caption="Simulation: n = 250, p = 100, 100 repetitions"
#     )
# )
# p1.show()
# # 실제로는 아무 변수도 y와 관련이 없는데도,
# # 먼저 100개 변수를 각각 검사한 뒤 유의한 것만 골라 최종 회귀를 하면,
# # 최종 모형의 p-value가 거의 0에 몰린다.


# p2=(
#     ggplot(sim_result, aes(x="num_selected"))
#     + geom_histogram(binwidth=1, boundary=0)
#     + labs(
#         title="Number of Predictors Selected by 100 Bivariate Tests",
#         subtitle="Each predictor is tested at alpha = 0.05",
#         x="Number of selected predictors",
#         y="Count"
#     )
# )
# p2.show()
# # 그냥 유의수준을 0.05로 잡은 탓에,
# # 약 5%의 설명변수들이 유의할 때가 압도적으로 자주 나온다.
# # 따라서 이 변수들은 우연에 의해 선택된 것이며,
# # 최종 회귀모형에 넣으면 전체 F검정의 p-value가 매우 작아진다.

# 9.9.4.

# import numpy as np
# import pandas as pd
# import statsmodels.formula.api as smf
# import statsmodels.api as sm

# from plotnine import (
#     ggplot, aes, geom_boxplot, geom_hline,
#     facet_wrap, labs
# )

# np.random.seed(123)
# NHANES=pd.read_csv("data/NHANES.csv")
# # a, b, c에서 사용할 변수는 Age, BMI, Diabetes뿐이므로 이렇게만 추출
# nhanes_female = (
#     NHANES
#     .loc[NHANES["Gender"].astype(str) == "female", ["Age", "BMI", "Diabetes"]]
#     .dropna(subset=["Age", "BMI", "Diabetes"])        # 결측치 제거
#     .assign(
#         diabetes=lambda df: np.where(df["Diabetes"] == "Yes", 1, 0)  # Y 가변수화
#     )
# )


# def fit_model(data):
#     # 주어진 데이터로 로지스틱 회귀 적합
#     return smf.glm(
#         formula="diabetes ~ Age + BMI",
#         data=data,
#         family=sm.families.Binomial()
#     ).fit()


# full_fit = fit_model(nhanes_female)       # 전체 적합 결과(True model)


# def model_summary(fit, label):
#     # 회귀계수, 표준오차, z통계량, p-value 추출
    
#     result = pd.DataFrame({
#         "mechanism": label,
#         "term": fit.params.index,
#         "estimate": fit.params.values,
#         "std_error": fit.bse.values,
#         "p_value": fit.pvalues.values
#     })
    
#     result["term"] = result["term"].replace({"Intercept": "(Intercept)"})
    
#     return result


# n_sample = int(np.floor(len(nhanes_female) / 10))     # 전체 자료의 10분의 1 크기를 표본 크기로 설정


# def simulate_missing(mechanism):
    
#     if mechanism == "MCAR":                           # a. MCAR 표본 추출
        
#         sampled_data = nhanes_female.sample(
#             n=n_sample,
#             replace=False
#         )                                             # 무작위로 1/10만 추출
    
#     elif mechanism == "CDM":                          # b. CDM 표본 추출
        
#         temp_data = nhanes_female.assign(
#             center_age=nhanes_female["Age"].median(), # 중앙값
#             scale_age=10                              # 감소 속도 조절값
#         )
        
#         temp_data = temp_data.assign(
#             observe_prob=lambda df: 1 / (
#                 1 + np.exp((df["Age"] - df["center_age"]) / df["scale_age"])
#             )
#             # 로지스틱 함수(0~1값), 나이가 많을수록 관측 가능성이 떨어짐
#         )
        
#         sampled_data = temp_data.sample(
#             n=n_sample,
#             replace=False,
#             weights="observe_prob"                    # 가중치를 다르게 줌으로써 확률 조정
#         )
    
#     elif mechanism == "NINR":                         # c. NINR 표본 추출
        
#         temp_data = nhanes_female.assign(
#             w_diabetes=0.5,                           # 당뇨자에게는 가중치 0.5 부여
#             observe_prob=lambda df: np.where(df["diabetes"] == 1, 0.5, 1)
#         )
        
#         sampled_data = temp_data.sample(
#             n=n_sample,
#             replace=False,
#             weights="observe_prob"                    # 당뇨자가 비당뇨자보다 덜 추출되도록 조절
#         )
    
#     fit = fit_model(sampled_data)
    
#     return model_summary(fit, mechanism)


# mechanism_order = ["Full", "MCAR", "CDM", "NINR"]

# full_result = model_summary(full_fit, "Full")
# full_result["mechanism"] = pd.Categorical(
#     full_result["mechanism"],
#     categories=mechanism_order,
#     ordered=True
# )


# sim_result = pd.concat(
#     [
#         pd.concat(
#             [
#                 simulate_missing("MCAR"),
#                 simulate_missing("CDM"),
#                 simulate_missing("NINR")
#             ],
#             ignore_index=True
#         ).assign(iteration=i)
#         for i in range(1, 101)                         # 100회 실행
#     ],
#     ignore_index=True
# )

# sim_result["mechanism"] = pd.Categorical(
#     sim_result["mechanism"],
#     categories=mechanism_order,
#     ordered=True
# )


# p=(
#     ggplot(sim_result, aes(x="mechanism", y="estimate"))
#     + geom_boxplot()                                  # 추출한 데이터 상자그림으로 시각화
#     + geom_hline(                                     # Full model의 값과 비교하기 용이하게
#         data=full_result,
#         mapping=aes(yintercept="estimate"),
#         size=0.5,
#         linetype="solid"
#     )
#     + facet_wrap("~ term", scales="free_y")
#     + labs(
#         title="Effect of Missing Data Mechanism on Logistic Regression Estimates",
#         subtitle="Solid line = Full data estimate",
#         x="Missing data mechanism",
#         y="Coefficient estimate",
#         caption="Source: NHANES package"
#     )
# )
# p.show()
# # 1. 표본 수 자체만 줄인 MCAR 방식은 전체적인 편향에 영향을 주지는 않지만 평균이 조금 흔들린다.

# # 2. CDM은 나이에 따라 가중치를 다르게 주었음에도 Age에서보다 BMI에서 큰 변화가 나타난다.
# # 이로부터 거시적으로는 Age와 BMI가 완전히 독립적으로 움직이지 않을 수 있음을 알 수 있다.
# # 고령층은 당뇨 비율이 높을 가능성이 크고, 동시에 BMI 분포도 젊은 층과 다를 수 있다.
# # 그러면 단순히 Age 계수만 흔들리는 게 아니라, BMI가 당뇨를 설명하는 방식도 함께 바뀐다.

# # 3. NINR에서는 (Intercept)에서 변화가 두드러지게 나타난다.
# # NINR에서는 코드상 당뇨 환자가 덜 관측되도록 했는데,
# # 이것이 전체적으로 당뇨 발생확률을 낮게 추정하게 되고
# # 그 결과 절편이 더 음수 방향으로 크게 이동했음을 알 수 있다.

# 9.9.7.

# import pandas as pd
# import numpy as np
# import statsmodels.api as sm
# import statsmodels.formula.api as smf

# from plotnine import (
#     ggplot, aes, geom_col, facet_wrap, labs
# )


# Whickham = sm.datasets.get_rdataset("Whickham", "mosaicData").data
# # Whickham DataFrame이 이미 준비되어 있다고 가정

# # 데이터 구조 확인
# Whickham.info()
# Whickham.head()

# # smoker: "No", "Yes" 확인
# overall_table = (
#     Whickham
#     .groupby(["smoker", "outcome"])
#     .size()
#     .reset_index(name="n")                         # 흡연여부/생존여부에 따라 분류
# )

# overall_table["prop"] = (
#     overall_table["n"] /
#     overall_table.groupby("smoker")["n"].transform("sum")
# )

# overall_table

# overall_death_rate = (
#     Whickham
#     .groupby("smoker")
#     .agg(
#         death_rate=("outcome", lambda x: np.mean(x == "Dead")),  # 흡연자/비흡연자의 사망확률
#         n=("outcome", "size")
#     )
#     .reset_index()
# )

# overall_death_rate

# p1=(
#     ggplot(overall_death_rate, aes(x="smoker", y="death_rate"))
#     + geom_col()
#     + labs(
#         title="Overall Death Rate of Smokers",
#         x="Smoker",
#         y="Death rate"
#     )
# )
# p1.show()
# # 나이를 고려하지 않고 결과만 본다면 흡연 여부가 수명에 악영향을 준다고 보기 어렵다.

# whickham_age = Whickham.copy()

# whickham_age["age_group"] = pd.cut(
#     whickham_age["age"],
#     bins=[0, 40, 50, 60, 70, np.inf],              # Whickham의 나이에 따른 층화 작업
#     labels=["<40", "40-49", "50-59", "60-69", "70+"],
#     right=False                                   # 오른쪽 끝값을 포함하지 않는 구간 설정
# )

# age_stratified_death_rate = (
#     whickham_age
#     .groupby(["age_group", "smoker"], observed=False)
#     .agg(
#         death_rate=("outcome", lambda x: np.mean(x == "Dead")),
#         n=("outcome", "size")
#     )
#     .reset_index()
# )

# age_stratified_death_rate

# p2 = (
#     ggplot(age_stratified_death_rate, aes(x="smoker", y="death_rate"))
#     + geom_col()
#     + facet_wrap("~ age_group")
#     + labs(
#         title="Mortality Rate by Smoking Status within Age Groups",
#         subtitle="Whickham data",
#         x="Smoking status",
#         y="Mortality rate"
#     )
# )
# p2.show()

# # 연령대가 같은 사람으로 봤을 때 흡연자의 사망률이 대부분 더 높다.
# # 따라서 흡연 여부가 수명에 악영향을 준다고 주장할 수 있다.

# # 로지스틱 모델을 통해 각 변수를 유의검정해보자
# whickham_model = Whickham.copy()

# whickham_model["dead"] = np.where(
#     whickham_model["outcome"] == "Dead",
#     1,
#     0
# )

# whickham_model["smoker"] = pd.Categorical(
#     whickham_model["smoker"],
#     categories=["No", "Yes"],
#     ordered=True
# )

# # 사망 여부 ~ 흡연 여부
# model_crude = smf.glm(
#     formula="dead ~ smoker",                     # 단순 전체 비교
#     data=whickham_model,
#     family=sm.families.Binomial()
# ).fit()

# # 사망 여부 ~ 흡연 여부 + 나이
# model_adjusted = smf.glm(
#     formula="dead ~ smoker + age",               # age를 교란변수로 보고 포함
#     data=whickham_model,
#     family=sm.families.Binomial()
# ).fit()

# model_crude.summary()
# model_adjusted.summary()

# # 나이별로 나누어 비교하거나 로지스틱 회귀에서 나이를 보정하면,
# # 단순한 전체 비교와 다른 결론이 나올 수 있다.
# # 따라서 이 자료에서는 흡연과 사망률의 관련성을 해석할 때 반드시 나이를 보정해야 한다.
# # 즉, 나이는 흡연 여부와 사망률 사이의 관계에서 교란변수로 작용한다.


# 7.9.5.
import pandas as pd
import matplotlib.pyplot as plt
from plotnine import (
    ggplot, aes, geom_jitter, geom_smooth,
    geom_boxplot, labs
)
from IPython.display import display

NHANES=pd.read_csv("data/NHANES.csv")

def pulse_plot(data, x_var):
    
    plot_data = (
        data[["Pulse", x_var]]
        .dropna()                         # Pulse 또는 x축 변수에 결측치가 있는 행 제거
    )
    
    return (
        ggplot(plot_data, aes(x=x_var, y="Pulse"))
        + geom_jitter(alpha=0.3)           # 점들이 겹치지 않게 약간 흩뿌려 산점도를 그림
        + geom_smooth(se=False, color="blue")            # Pulse와 x축 변수 사이의 전반적 추세선을 그림
        + labs(
            title=f"Pulse by {x_var}",
            subtitle="source = NHANES",
            x=x_var,
            y="Pulse"
        )
    )


pulse_vars = ["Age", "BMI", "BPSysAve"]    # Pulse와 비교할 변수들

pulse_plots = [
    pulse_plot(NHANES, x_var)
    for x_var in pulse_vars
]

for p in pulse_plots:
    p.show()

# Pulse는 Age, BMI, BPSysAve와 강한 선형관계를 보이지 않는다.
# 얼추 직선을 띠는 변수들도 있으나 그 산포도가 너무 커 신뢰도가 낮다.


# 변수 중 TVHrsDay는 0_hours..처럼 범주형 변수로 분류된다.
# 따라서 각 변수마다 상자그림을 통해 분포를 알아본다.
tv_plot_data = (
    NHANES[["Pulse", "TVHrsDay"]]
    .dropna()
)

p=(
    ggplot(tv_plot_data, aes(x="TVHrsDay", y="Pulse"))
    + geom_boxplot()
    + geom_jitter(alpha=0.2, width=0.2)     # 점이 지나치게 겹쳐보이지 않게 산포
    + labs(
        title="Pulse by TVHrsDay",
        subtitle="NHANES",
        x="TV hours per day",
        y="Pulse"
    )
)

p.show()
# TVHrsDay도 마찬가지로 강한 상관관계를 띠지는 않는다.







