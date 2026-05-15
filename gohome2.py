
import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf

from plotnine import (
    ggplot, aes, geom_col, facet_wrap, labs
)


Whickham = sm.datasets.get_rdataset("Whickham", "mosaicData").data
# Whickham DataFrame이 이미 준비되어 있다고 가정

# 데이터 구조 확인
Whickham.info()
Whickham.head()

# smoker: "No", "Yes" 확인
overall_table = (
    Whickham
    .groupby(["smoker", "outcome"])
    .size()
    .reset_index(name="n")                         # 흡연여부/생존여부에 따라 분류
)

overall_table["prop"] = (
    overall_table["n"] /
    overall_table.groupby("smoker")["n"].transform("sum")
)

overall_table

overall_death_rate = (
    Whickham
    .groupby("smoker")
    .agg(
        death_rate=("outcome", lambda x: np.mean(x == "Dead")),  # 흡연자/비흡연자의 사망확률
        n=("outcome", "size")
    )
    .reset_index()
)

overall_death_rate

p1=(
    ggplot(overall_death_rate, aes(x="smoker", y="death_rate"))
    + geom_col()
    + labs(
        title="Overall Death Rate of Smokers",
        x="Smoker",
        y="Death rate"
    )
)
p1.show()
# 나이를 고려하지 않고 결과만 본다면 흡연 여부가 수명에 악영향을 준다고 보기 어렵다.

whickham_age = Whickham.copy()

whickham_age["age_group"] = pd.cut(
    whickham_age["age"],
    bins=[0, 40, 50, 60, 70, np.inf],              # Whickham의 나이에 따른 층화 작업
    labels=["<40", "40-49", "50-59", "60-69", "70+"],
    right=False                                   # 오른쪽 끝값을 포함하지 않는 구간 설정
)

age_stratified_death_rate = (
    whickham_age
    .groupby(["age_group", "smoker"], observed=False)
    .agg(
        death_rate=("outcome", lambda x: np.mean(x == "Dead")),
        n=("outcome", "size")
    )
    .reset_index()
)

age_stratified_death_rate

p2 = (
    ggplot(age_stratified_death_rate, aes(x="smoker", y="death_rate"))
    + geom_col()
    + facet_wrap("~ age_group")
    + labs(
        title="Mortality Rate by Smoking Status within Age Groups",
        subtitle="Whickham data",
        x="Smoking status",
        y="Mortality rate"
    )
)
p2.show()

# 연령대가 같은 사람으로 봤을 때 흡연자의 사망률이 대부분 더 높다.
# 따라서 흡연 여부가 수명에 악영향을 준다고 주장할 수 있다.

# 로지스틱 모델을 통해 각 변수를 유의검정해보자
whickham_model = Whickham.copy()

whickham_model["dead"] = np.where(
    whickham_model["outcome"] == "Dead",
    1,
    0
)

whickham_model["smoker"] = pd.Categorical(
    whickham_model["smoker"],
    categories=["No", "Yes"],
    ordered=True
)

# 사망 여부 ~ 흡연 여부
model_crude = smf.glm(
    formula="dead ~ smoker",                     # 단순 전체 비교
    data=whickham_model,
    family=sm.families.Binomial()
).fit()

# 사망 여부 ~ 흡연 여부 + 나이
model_adjusted = smf.glm(
    formula="dead ~ smoker + age",               # age를 교란변수로 보고 포함
    data=whickham_model,
    family=sm.families.Binomial()
).fit()

model_crude.summary()
model_adjusted.summary()

# 나이별로 나누어 비교하거나 로지스틱 회귀에서 나이를 보정하면,
# 단순한 전체 비교와 다른 결론이 나올 수 있다.
# 따라서 이 자료에서는 흡연과 사망률의 관련성을 해석할 때 반드시 나이를 보정해야 한다.
# 즉, 나이는 흡연 여부와 사망률 사이의 관계에서 교란변수로 작용한다.
