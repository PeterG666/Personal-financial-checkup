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
        actions.append("先让现金流转正：逐项核对基本开销与每月还款，暂停新增消费性负债，并为支出设上限。")
    if d["essential_outflow"] == 0:
        actions.append("补全支出口径：检查房租、保险、生活费等是否遗漏，或确认目前由他人承担；缺少必要支出时无法估算安全垫。")
    if d["emergency_months"] is not None and d["emergency_months"] < d["emergency_target"]:
        gap = max(0, d["emergency_target"] * d["essential_outflow"] - data["liquid_assets"])
        actions.append(f"建立应急缓冲：按当前支出与还款，目标为 {d['emergency_target']} 个月，尚差约 {money(gap)}。优先放在随时可用、低波动的账户。")
    if (d["debt_service_rate"] is not None and d["debt_service_rate"] > 35) or (not data["monthly_income"] and data["monthly_debt_payment"]):
        actions.append("梳理债务：列出每笔利率、月供和到期日，评估还款来源；提前还款前同时考虑违约费用与应急资金需求。")
    if d["net_worth"] is not None and d["net_worth"] < 0:
        actions.append("复核净资产：目前债务本金大于已填资产。检查是否漏填自住房等资产，并按可实现的现值重新核对。")
    if d["savings_rate"] is not None and d["savings_rate"] < 30 and d["monthly_surplus"] > 0:
        amount = min(d["monthly_surplus"], data["monthly_income"] * .3)
        actions.append(f"让储蓄可持续：按当前收支，月度储蓄可先以不超过 {money(amount)} 为讨论起点。先记账一个月，确认偶发支出后再安排自动转存。")
    if not actions and d["monthly_surplus"] == 0:
        actions.append("为现金流留出余量：当前收入刚好覆盖支出，可先核对非必要开支，逐步建立每月结余。")
    if d["net_worth"] is None:
        actions.append("补全债务本金：确认各笔贷款的剩余本金后重新提交，才能评估家庭净资产；没有债务时填写 0。")
    if not actions:
        actions.append("维持当前结构：每季度复核一次收支、负债和资产配置；收入、家庭责任或目标发生变化时及时更新。")
    return actions[:3]


st.markdown("<div class='eyebrow'>PERSONAL FINANCE CHECKUP</div>", unsafe_allow_html=True)
st.title("把家庭财务，理清楚一点")
st.markdown("<p class='lede'>用几分钟整理收支与资产，看见财务现状，找到下一步。<br>01 填写数据　→　02 查看体检　→　03 制定行动</p>", unsafe_allow_html=True)

with st.form("financial_input", clear_on_submit=False):
    st.subheader("填写你的财务数据")
    st.caption("以个人或家庭为统一口径，所有金额单位均为人民币元。初始数字仅供示例，请替换为实际情况。")
    st.markdown("<div class='section-label'>01 / 每月收支</div>", unsafe_allow_html=True)
    income_col, expense_col, savings_col = st.columns(3)
    with income_col:
        monthly_income = st.number_input("每月税后总收入（元）", min_value=0.0, value=15000.0, step=500.0, help="家庭每月到手收入总额。")
    with expense_col:
        monthly_expense = st.number_input("每月生活总支出（不含还贷，元）", min_value=0.0, value=8000.0, step=500.0, help="包括必要与可选消费：房租、餐饮、交通、娱乐等；年度保费等折算到每月。不包含储蓄、投资转账和债务还款。")
    with savings_col:
        monthly_savings = st.number_input("每月新增储蓄／投资（元）", min_value=0.0, value=3000.0, step=500.0, help="仅填本月收入中留下的钱，不含已有存款搬家、借款或投资市值涨幅。")
    st.markdown("<div class='section-label'>02 / 资产与负债</div>", unsafe_allow_html=True)
    st.caption("每笔资产只计一次，按当前估值填写：应急资金 → 其余投资资产 → 自用资产。房屋按全值填入，贷款本金在负债中扣除。")
    asset_col_1, asset_col_2, asset_col_3 = st.columns(3)
    with asset_col_1:
        liquid_assets = st.number_input("流动资产（元）", min_value=0.0, value=30000.0, step=1000.0, help="现金、活期、货币基金等可较快动用的资金。")
    with asset_col_2:
        earning_assets = st.number_input("其他生息／投资资产（元）", min_value=0.0, value=20000.0, step=1000.0, help="不含左侧已填的流动资产。如长期存款、债券、基金、股票、出租房产。")
    with asset_col_3:
        other_assets = st.number_input("自用或其他资产（元）", min_value=0.0, value=30000.0, step=1000.0, help="包括自住房、车辆等，按当前合理变现价值填写，而非买入价。")
    debt_col_1, debt_col_2, occupation_col = st.columns(3)
    with debt_col_1:
        monthly_debt_payment = st.number_input("每月债务还款（元）", min_value=0.0, value=4000.0, step=500.0, help="房贷、车贷、消费贷、分期等每月必须还款。")
    with debt_col_2:
        remaining_debt = st.number_input("剩余债务本金（元，可留空）", min_value=0.0, value=None, step=10000.0, placeholder="无债务填 0，未知留空", help="留空时不计算净资产。包括住房、汽车及其他贷款尚未偿还的本金。")
    with occupation_col:
        emergency_target = st.selectbox("应急储备目标（月）", [3, 6, 9, 12], index=1, help="按收入稳定性、家庭责任与实际支出选择；收入波动大或责任较重时可考虑更长缓冲期。")
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
        errors.append("新增储蓄超过扣除生活支出和还款后的结余，请核对是否重复计算，或把已有资金转账当作新增储蓄。")
    if remaining_debt == 0 and monthly_debt_payment > 0:
        errors.append("已填写每月还款，但剩余债务为 0。请核对本金；未知时可清空该项。")
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
earning_status, earning_css = "结构观察", "neutral"
safe_count = sum(status == "稳健" for status in [emergency_status, savings_status, debt_status])
critical = (d["monthly_surplus"] < 0 or emergency_css == "bad" or debt_css == "bad" or (d["net_worth"] is not None and d["net_worth"] < 0))

if critical:
    summary_class, summary_title = "risk", "先稳住现金流与安全边际"
    summary_text = "当前现金流、安全垫、月供或净资产中至少有一项需要优先关注。可先从下方行动建议着手，逐步减少刚性压力。"
elif safe_count == 3 and d["net_worth"] is not None:
    summary_class, summary_title = "good", "三项基础指标达到当前参考目标"
    summary_text = "安全垫、储蓄和月供比例达到当前参考目标。定期复核家庭目标与收支；这不代表投资收益或整体财务安全得到保证。"
else:
    summary_class, summary_title = "watch", "还有值得补充与调整的地方"
    summary_text = "查看下方具体指标，优先补全数据、确认可持续结余与应急储备。投资资产占比仅作结构观察，不参与健康评级。"

st.markdown("<div class='section-label'>你的专属报告</div>", unsafe_allow_html=True)
st.caption(f"生成于 {st.session_state['report_time']} · 以下结果基于最近一次提交。修改表单后，请重新点击生成按钮。")
st.markdown(f"<div class='summary-card {summary_class}'><div class='summary-kicker'>FINANCIAL SNAPSHOT</div><div class='summary-title'>{summary_title}</div><div class='summary-text'>{summary_text}</div></div>", unsafe_allow_html=True)
overview = st.columns(4)
overview[0].metric("储蓄前月度结余", money(d["monthly_surplus"]), help="月收入 − 生活总支出 − 每月债务还款；储蓄是结余的去向，不重复扣除。")
overview[1].metric("家庭净资产", money(d["net_worth"]) if d["net_worth"] is not None else "待补全债务", help="总资产 − 剩余债务本金；未知本金时不估算。")
overview[2].metric("月支出与还款", money(d["essential_outflow"]))
overview[3].metric("总资产", money(d["total_assets"]))
if d["net_worth"] is None:
    st.caption("剩余债务本金尚未填写，净资产暂不可评估。")
unallocated = d["monthly_surplus"] - data["monthly_savings"]
if unallocated > .01:
    st.caption(f"结余中有 {money(unallocated)} 尚未计入新增储蓄，可核对是否有遗漏支出或待分配资金。")

st.subheader("四项核心检查")
left, right = st.columns(2, gap="large")
with left:
    metric_block("安全垫", f"{d['emergency_months']:.1f} 个月" if d['emergency_months'] is not None else "暂不可计算", emergency_status, emergency_css, f"流动资产 ÷（生活总支出 + 月供）；你选择的目标为 {d['emergency_target']} 个月。", "按维持当前生活开支估算缓冲时间。没有支出数据时无法测算，收入稳定性与家庭责任也应纳入考虑。")
    metric_block("储蓄力", f"{d['savings_rate']:.1f}%" if d['savings_rate'] is not None else "暂不可计算", savings_status, savings_css, "每月新增储蓄／投资 ÷ 税后总收入；本工具参考目标为 30%。", "稳定、可持续的储蓄，是建立安全垫和长期资金的共同起点。30% 是自查参考值，并非人人必须达到的标准。")
with right:
    metric_block("债务压力", f"{d['debt_service_rate']:.1f}%" if d['debt_service_rate'] is not None else "暂无收入基数", debt_status, debt_css, "每月债务还款 ÷ 税后总收入；35% 和 50% 为本工具的提醒界线。", "还款比例只是一个维度，还需结合利率、到期日与生活支出判断；零收入时不把月供比例记为零。")
    metric_block("其他投资资产占比", f"{d['earning_ratio']:.1f}%" if d['earning_ratio'] is not None else "暂无资产", earning_status, earning_css, "其他生息／投资资产 ÷ 总资产；不含已归入流动资产的部分。", "仅展示结构，不设统一及格线。合适的配置取决于资金用途、期限与风险承受能力，不能从占比推断收益。")

st.subheader("接下来，优先做这几件事")
for index, action in enumerate(build_actions(d, data), start=1):
    st.markdown(f"**{index:02d}**　{action}")

with st.expander("查看计算口径与使用说明"):
    st.markdown("- 应急目标由你选择；储蓄率 30%、月供比例 35%／50% 是本工具的自查参考，不是普适标准。\n- 每笔资产只填一次；自住房计入自用资产，不计入应急资金。\n- 本次报告仅反映已填数据，未评估保险保障、负债利率、税务或投资集中度。\n- 内容沿用原应用的财务自查框架并调整表述，未逐条核验课程音频。\n\n参考：[CFPB：应急资金](https://www.consumerfinance.gov/an-essential-guide-to-building-an-emergency-fund/) · [Investor.gov：资产配置](https://www.investor.gov/introduction-investing/getting-started/asset-allocation)")
st.markdown("<p class='disclaimer'>本工具用于个人财务教育与自我梳理，报告基于你填写的数据和通用参考口径生成，不构成投资、信贷或法律建议。</p>", unsafe_allow_html=True)
