import math
from datetime import datetime

import streamlit as st


st.set_page_config(
    page_title="家庭财务体检｜清晰看见每一笔钱",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        :root { --ink: #15231D; --muted: #68756F; --line: #DCE5DE; --paper: #F7F8F4;
                --green: #176B4A; --soft-green: #EAF4ED; --gold: #B87921; --red: #B7413E; }
        .stApp { background: var(--paper); color: var(--ink); }
        .block-container { max-width: 1180px; padding-top: 3.3rem; padding-bottom: 4rem; }
        h1, h2, h3 { color: var(--ink) !important; letter-spacing: -0.025em; }
        h1 { font-size: 2.35rem !important; margin-bottom: .45rem !important; }
        h2 { margin-top: 1.8rem !important; }
        .eyebrow { color: var(--green); font-size: .78rem; letter-spacing: .12em; font-weight: 700; }
        .lede { color: var(--muted); font-size: 1.05rem; max-width: 680px; line-height: 1.7; }
        [data-testid="stForm"] { background: #FFFFFF; border: 1px solid var(--line); border-radius: 18px;
                                     padding: 1.25rem 1.5rem; }
        .section-label { color: var(--green); font-size: .78rem; font-weight: 700; letter-spacing: .08em;
                          text-transform: uppercase; margin: .4rem 0 .1rem; }
        .summary-card { border-radius: 18px; padding: 1.55rem 1.7rem; color: white; margin: 1rem 0 1.25rem; }
        .summary-card.good { background: linear-gradient(125deg, #145C43, #278159); }
        .summary-card.watch { background: linear-gradient(125deg, #89601D, #B9842E); }
        .summary-card.risk { background: linear-gradient(125deg, #8F3737, #BF5751); }
        .summary-kicker { font-size: .78rem; opacity: .8; letter-spacing: .1em; font-weight: 700; }
        .summary-title { font-size: 1.65rem; font-weight: 700; margin: .3rem 0 .4rem; }
        .summary-text { opacity: .93; line-height: 1.65; }
        .metric-note { color: var(--muted); font-size: .88rem; line-height: 1.55; }
        .status { display: inline-block; padding: .2rem .6rem; border-radius: 999px; font-size: .78rem; font-weight: 700; }
        .ok { color: #0E5A3D; background: #DDF2E5; } .warn { color: #80570E; background: #FFF0CC; }
        .bad { color: #8A2929; background: #FCE2E0; }
        .neutral { color: #53676A; background: #EAF0F0; }
        [data-testid="stMetric"] { background: #fff; border: 1px solid var(--line); border-radius: 14px; padding: .8rem 1rem; }
        [data-testid="stMetricLabel"] { color: var(--muted); }
        div[data-testid="stFormSubmitButton"] button { background: var(--green); border: 0; min-height: 2.8rem;
                                                        color: white; font-weight: 700; border-radius: 9px; }
        div[data-testid="stFormSubmitButton"] button:hover { background: #0D5137; }
        .disclaimer { color: var(--muted); font-size: .82rem; line-height: 1.6; }
        @media (max-width: 640px) {
            .block-container { padding: 1.7rem 1rem; }
            h1 { font-size: 1.8rem !important; }
            .summary-title { font-size: 1.35rem; }
            .summary-card { padding: 1.25rem; }
            [data-testid="stCaptionContainer"] { font-size: .88rem; line-height: 1.6; }
            [data-testid="stForm"] { padding: 1rem; }
            [data-testid="stHorizontalBlock"] { flex-wrap: wrap; }
            [data-testid="stColumn"] { min-width: 100% !important; width: 100% !important; flex: 1 1 100% !important; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def money(value: float) -> str:
    return f"¥{value:,.0f}"


def amount_input(label: str, explanation: str, **kwargs):
    """Keep instructions in normal page flow so touch users need no tooltip."""
    value = st.number_input(label, min_value=0.0, **kwargs)
    st.caption(explanation)
    return value


def status_for(value: float, good: float, caution: float, reverse: bool = False) -> tuple[str, str]:
    if reverse:
        if value <= good:
            return "稳健", "ok"
        if value <= caution:
            return "留意", "warn"
        return "优先处理", "bad"
    if value >= good:
        return "稳健", "ok"
    if value >= caution:
        return "留意", "warn"
    return "优先处理", "bad"


def diagnostic(data: dict) -> dict:
    essential_outflow = data["monthly_expense"] + data["monthly_debt_payment"]
    emergency_months = data["liquid_assets"] / essential_outflow if essential_outflow else None
    savings_rate = data["monthly_savings"] / data["monthly_income"] * 100 if data["monthly_income"] else None
    debt_service_rate = data["monthly_debt_payment"] / data["monthly_income"] * 100 if data["monthly_income"] else None
    total_assets = data["liquid_assets"] + data["earning_assets"] + data["other_assets"]
    earning_ratio = data["earning_assets"] / total_assets * 100 if total_assets else None
    monthly_surplus = data["monthly_income"] - essential_outflow
    net_worth = total_assets - data["remaining_debt"] if data["remaining_debt"] is not None else None
    emergency_target = data["emergency_target"]
    return {
        "essential_outflow": essential_outflow, "emergency_months": emergency_months,
        "emergency_target": emergency_target, "savings_rate": savings_rate,
        "debt_service_rate": debt_service_rate, "earning_ratio": earning_ratio,
        "total_assets": total_assets, "monthly_surplus": monthly_surplus, "net_worth": net_worth,
    }


def metric_block(title: str, value: str, status: str, css: str, formula: str, note: str) -> None:
    st.markdown(f"#### {title}  <span class='status {css}'>{status}</span>", unsafe_allow_html=True)
    st.metric("当前水平", value)
    st.caption(formula)
    st.markdown(f"<p class='metric-note'>{note}</p>", unsafe_allow_html=True)


def build_actions(d: dict, data: dict) -> list[str]:
    actions = []
    if d["monthly_surplus"] < 0:
        actions.append(f"先解决入不敷出：按你填的数据，每月还差 {money(-d['monthly_surplus'])}。看看哪些开销可以减少，避免继续借钱补日常花费。")
    if d["essential_outflow"] == 0:
        actions.append("检查有没有漏填花费：房租、保险、生活费是否由别人承担？每月花多少钱还不清楚，就算不出存款能用多久。")
    if d["emergency_months"] is not None and d["emergency_months"] < d["emergency_target"]:
        gap = max(0, d["emergency_target"] * d["essential_outflow"] - data["liquid_assets"])
        actions.append(f"攒一笔急用钱：要覆盖 {d['emergency_target']} 个月的生活费和还款，尚差约 {money(gap)}。这笔钱要容易取用，尽量避免本金大幅涨跌。")
    if (d["debt_service_rate"] is not None and d["debt_service_rate"] > 35) or (not data["monthly_income"] and data["monthly_debt_payment"]):
        actions.append("把欠款列清楚：每笔还欠多少、利息多少、每月还多少、哪天还。提前还款前，先确认有没有额外费用，也要留够急用的钱。")
    if d["net_worth"] is not None and d["net_worth"] < 0:
        actions.append("核对家底和欠款：目前填的欠款超过全部家当的估价。看看有没有漏填自己的房子，并按现在大概能卖多少钱重新核对。")
    if d["savings_rate"] is not None and d["savings_rate"] < 30 and d["monthly_surplus"] > 0:
        amount = min(d["monthly_surplus"], data["monthly_income"] * .3)
        actions.append(f"定一个做得到的存钱目标：按当前收支，可先在每月 {money(amount)} 以内考虑。先记账一个月，给临时花费留出余地，再决定固定存多少。")
    if not actions and d["monthly_surplus"] == 0:
        actions.append("争取每月留下一点钱：目前收入刚好够花和还款，看看有没有可以减少的非必要开销。")
    if d["net_worth"] is None:
        actions.append("补填还欠多少钱：在银行或贷款账单中查看“剩余本金”，填完后就能算出扣掉欠款还剩多少家底；没有欠款填 0。")
    if not actions:
        actions.append("每隔三个月再看一次：收入、开销、欠款有变化，或家里有了新的用钱计划，就重新算一遍。")
    return actions[:3]


st.markdown("<div class='eyebrow'>PERSONAL FINANCE CHECKUP</div>", unsafe_allow_html=True)
st.title("把家庭财务，理清楚一点")
st.markdown("<p class='lede'>用几分钟，看看钱够不够花、存得够不够，再想想下一步怎么做。<br>01 填写数据　→　02 查看结果　→　03 看看建议</p>", unsafe_allow_html=True)

with st.form("financial_input", clear_on_submit=False):
    st.subheader("填写你的财务数据")
    st.caption("可以只算你自己，也可以算全家，但下面都要按同一种方式填写。金额都是人民币元，示例数字请换成你的实际情况。")
    st.markdown("<div class='section-label'>01 / 每月收支</div>", unsafe_allow_html=True)
    income_col, expense_col, savings_col = st.columns(3)
    with income_col:
        monthly_income = amount_input("每月实际到手的钱（元）", "工资、养老金等实际到账的收入加起来；如果算全家，就把家人的收入也加上。", value=15000.0, step=500.0)
    with expense_col:
        monthly_expense = amount_input("每月生活花费（不含还款，元）", "吃饭、房租、水电、交通、购物等。一年交一次的保费除以 12；存钱、投资和还款不填这里。", value=8000.0, step=500.0)
    with savings_col:
        monthly_savings = amount_input("每月新存下或用于投资的钱（元）", "只算从这个月收入里留下的钱。旧存款换账户、借来的钱、基金上涨赚到的钱，都不算。", value=3000.0, step=500.0)
    st.markdown("<div class='section-label'>02 / 现有的钱、家当和欠款</div>", unsafe_allow_html=True)
    st.caption("同一笔钱或家当只填一次。房子、车等按现在大概能卖多少钱填，先不扣贷款；欠款在下面单独填写。")
    asset_col_1, asset_col_2, asset_col_3 = st.columns(3)
    with asset_col_1:
        liquid_assets = amount_input("现在能拿来应急的钱（元）", "如现金、银行卡活期、能及时取出的余额宝。股票、房子和不能及时取出的存款不填这里。", value=30000.0, step=1000.0)
    with asset_col_2:
        earning_assets = amount_input("另外存着或投资的钱（元）", "如定期存款、股票、基金、债券、出租的房子，按当前金额或估价填。已填的应急钱不要再加一次。", value=20000.0, step=1000.0)
    with asset_col_3:
        other_assets = amount_input("自己用的房子、车等值多少（元）", "把自住房、车等现在大概能卖的钱加起来，不是当初买的价格。已填过的家当不要重复算。", value=30000.0, step=1000.0)
    debt_col_1, debt_col_2, occupation_col = st.columns(3)
    with debt_col_1:
        monthly_debt_payment = amount_input("每月要还的钱（元）", "房贷、车贷、消费贷、分期等每月实际要还的总额，包括本金和利息；不要再计入生活花费。", value=4000.0, step=500.0)
    with debt_col_2:
        remaining_debt = amount_input("一共还欠多少钱（元，可留空）", "查看贷款账单上的“剩余本金”并加起来，不含未来利息。没有欠款填 0；不知道可留空。", value=None, step=10000.0, placeholder="没有欠款填 0，不知道留空")
    with occupation_col:
        emergency_target = st.selectbox("想留够几个月的急用钱？", [3, 6, 9, 12], index=1)
        st.caption("假设暂时没有收入，这笔钱要够生活和还款多久？收入不稳定或要照顾家人时，可考虑多留一些。")
    submitted = st.form_submit_button("生成我的财务体检报告", type="primary", use_container_width=True)

if submitted:
    candidate = {
        "monthly_income": monthly_income, "monthly_expense": monthly_expense, "monthly_savings": monthly_savings,
        "liquid_assets": liquid_assets, "earning_assets": earning_assets, "other_assets": other_assets,
        "monthly_debt_payment": monthly_debt_payment, "remaining_debt": remaining_debt, "emergency_target": emergency_target,
    }
    errors = []
    if any(value is not None and (not math.isfinite(value) or value < 0) for value in candidate.values()):
        errors.append("金额必须是有效的非负数字。")
    if monthly_savings > max(0, monthly_income - monthly_expense - monthly_debt_payment) + .01:
        errors.append("你填的新存下的钱，比收入减去生活花费和还款后剩下的钱还多。请检查是否把旧存款转账算了进来，或重复填了花费。")
    if remaining_debt == 0 and monthly_debt_payment > 0:
        errors.append("你填了每月要还钱，但一共欠款却是 0。请核对账单；不知道一共还欠多少，可以把这一项清空。")
    if errors:
        for error in errors:
            st.error(error)
        st.info("本次未生成报告。修正后重新提交；此前报告暂不展示。")
        st.stop()
    st.session_state["report_input"] = candidate
    st.session_state["report_time"] = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")

if "report_input" not in st.session_state:
    st.info("填写上方数据后，点击“生成我的财务体检报告”。报告只会在你主动提交后更新。")
    st.stop()

data = st.session_state["report_input"]
d = diagnostic(data)
emergency_status, emergency_css = status_for(d["emergency_months"], d["emergency_target"], d["emergency_target"] * 0.6) if d["emergency_months"] is not None else ("待补充支出", "warn")
savings_status, savings_css = status_for(d["savings_rate"], 30, 15) if d["savings_rate"] is not None else ("暂无收入", "warn")
debt_status, debt_css = status_for(d["debt_service_rate"], 35, 50, reverse=True) if d["debt_service_rate"] is not None else (("优先处理", "bad") if data["monthly_debt_payment"] else ("无月供", "ok"))
earning_css = "neutral"
safe_count = sum(status == "稳健" for status in [emergency_status, savings_status, debt_status])
critical = (d["monthly_surplus"] < 0 or emergency_css == "bad" or debt_css == "bad" or (d["net_worth"] is not None and d["net_worth"] < 0))

if critical:
    summary_class, summary_title = "risk", "先顾好日常开销，留够急用钱"
    summary_text = "按你填的数据，可能存在钱不够花、应急钱偏少、还款较多，或欠款超过家当估价的情况。下面会告诉你具体是哪一项，以及可以先做什么。"
elif safe_count == 3 and d["net_worth"] is not None:
    summary_class, summary_title = "good", "应急钱、存钱和还款情况较好"
    summary_text = "这三项都达到了当前参考目标。可以继续保持，并在收入或开销变化时重新算一遍；这不代表投资一定赚钱。"
else:
    summary_class, summary_title = "watch", "还有值得补充与调整的地方"
    summary_text = "先看每月能剩多少钱、急用钱够不够，再把不知道的欠款补齐。投资占多少只帮助你了解钱放在哪里，不用它判断好坏。"

st.markdown("<div class='section-label'>你的专属报告</div>", unsafe_allow_html=True)
st.caption(f"生成于 {st.session_state['report_time']} · 以下结果基于最近一次提交。修改表单后，请重新点击生成按钮。")
st.markdown(f"<div class='summary-card {summary_class}'><div class='summary-kicker'>FINANCIAL SNAPSHOT</div><div class='summary-title'>{summary_title}</div><div class='summary-text'>{summary_text}</div></div>", unsafe_allow_html=True)
overview = st.columns(4)
overview[0].metric("每月花完、还完后剩下的钱", money(d["monthly_surplus"]))
overview[0].caption("到手收入减去生活花费和还款。存下的钱就在这里面，不再扣一次；负数表示不够花。")
overview[1].metric("扣掉欠款后，还剩多少家底", money(d["net_worth"]) if d["net_worth"] is not None else "还没填欠款")
overview[1].caption("全部钱和家当的估价减去欠款，也叫“净资产”。房子、车等不一定能马上换成现金。")
overview[2].metric("每月花费和还款共多少", money(d["essential_outflow"]))
overview[2].caption("每月生活花费加上要还的钱。")
overview[3].metric("全部钱和家当的估价", money(d["total_assets"]))
overview[3].caption("你填的三类钱和家当加起来，还没有扣掉欠款。")
if d["net_worth"] is None:
    st.caption("还不知道一共欠多少，所以暂时算不出扣掉欠款后的家底。")
unallocated = d["monthly_surplus"] - data["monthly_savings"]
if unallocated > .01:
    st.caption(f"每月剩下的钱里，还有 {money(unallocated)} 没计入新存下的钱。看看是花费漏填了，还是这笔钱还没安排用途。")

st.subheader("这四件事，帮你看明白")
left, right = st.columns(2, gap="large")
with left:
    metric_block(
        "如果暂时没收入，存款能撑多久？",
        f"{d['emergency_months']:.1f} 个月" if d['emergency_months'] is not None else "暂不可计算",
        emergency_status, emergency_css,
        f"你有 {money(data['liquid_assets'])} 可应急，每月生活和还款共 {money(d['essential_outflow'])}。",
        f"假设没有新收入、花费保持不变，上面的月数就是这笔钱大概能用多久。你希望备够 {d['emergency_target']} 个月。这就是常说的应急钱或“安全垫”。" if d['emergency_months'] is not None else "你填的每月花费和还款都是 0，暂时算不出能撑多久，请先核对是否漏填。",
    )
    metric_block(
        "每收入 100 元，能存下多少？",
        f"{d['savings_rate']:.1f} 元" if d['savings_rate'] is not None else "暂不可计算",
        savings_status, savings_css,
        f"每月到手 {money(data['monthly_income'])}，其中新存下或用于投资 {money(data['monthly_savings'])}。",
        "例如，显示 20 元，就表示每收入 100 元留下了 20 元，也叫储蓄率 20%。本工具以 30 元作参考，不必勉强，先保证日常生活。" if d['savings_rate'] is not None else "当前没有收入，所以算不出每收入 100 元能存多少。",
    )
with right:
    metric_block(
        "每收入 100 元，要拿多少还款？",
        f"{d['debt_service_rate']:.1f} 元" if d['debt_service_rate'] is not None else "暂无收入基数",
        debt_status, debt_css,
        f"每月到手 {money(data['monthly_income'])}，要还 {money(data['monthly_debt_payment'])}。",
        "例如，显示 40 元，就表示收入的四成要用来还款。本工具在超过 35 元、50 元时分别提醒；还要看剩下的钱够不够生活。" if d['debt_service_rate'] is not None else "没有收入时不能计算比例；如果仍需还款，要先确认用什么钱还。",
    )
    metric_block(
        "家底中，有多少另外存着或用于投资？",
        f"{d['earning_ratio']:.1f}%" if d['earning_ratio'] is not None else "暂无资产",
        "了解分布", earning_css,
        f"另外存着或投资的 {money(data['earning_assets'])}，占全部钱和家当 {money(d['total_assets'])} 的比例。",
        "例如，25% 就是四分之一。这里不含已填的应急钱，只帮你了解钱放在哪里；比例高不代表一定赚钱，低也不代表不好。" if d['earning_ratio'] is not None else "你还没有填写钱或家当，所以暂时没有比例可看。",
    )

st.subheader("接下来，优先做这几件事")
for index, action in enumerate(build_actions(d, data), start=1):
    st.markdown(f"**{index:02d}**　{action}")

with st.expander("这些结果怎么算？"):
    st.markdown("- **急用钱能撑多久**：能拿来应急的钱 ÷ 每月生活花费与还款。想备够几个月，由你自己选择。\n- **每收入 100 元能存多少**：每月新存下的钱 ÷ 每月到手收入 × 100。30 元只是参考，不是人人必须达到。\n- **每收入 100 元要还多少**：每月还款 ÷ 每月到手收入 × 100。本工具超过 35 元时提醒留意，超过 50 元时提醒优先处理。\n- **扣掉欠款后的家底**：全部钱和家当的估价 − 还欠的本金。同一笔钱、房子或车不要重复填写。\n- 报告只根据已填信息计算，还没有考虑保险够不够、贷款利息多不多等情况。\n\n延伸阅读：[应急钱怎样准备](https://www.consumerfinance.gov/an-essential-guide-to-building-an-emergency-fund/) · [投资如何分配](https://www.investor.gov/introduction-investing/getting-started/asset-allocation)")
st.markdown("<p class='disclaimer'>本工具用于个人财务教育与自我梳理，报告基于你填写的数据和通用参考口径生成，不构成投资、信贷或法律建议。</p>", unsafe_allow_html=True)
