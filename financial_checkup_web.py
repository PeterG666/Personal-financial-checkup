import streamlit as st
import pandas as pd

# 设置网页配置
st.set_page_config(
    page_title="家庭财务健康深度诊断系统 - 董小姐理财系列",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS 样式
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        color: #1E3A8A;
        font-weight: bold;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #4B5563;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        padding: 1.5rem;
        border-radius: 0.75rem;
        border-left: 5px solid #1E3A8A;
        margin-bottom: 1rem;
    }
    .metric-title {
        font-size: 1.1rem;
        color: #374151;
        font-weight: bold;
    }
    .metric-value {
        font-size: 1.8rem;
        color: #1E3A8A;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: bold;
        text-align: center;
    }
    .badge-pass {
        background-color: #D1FAE5;
        color: #065F46;
    }
    .badge-warn {
        background-color: #FEF3C7;
        color: #92400E;
    }
    .badge-fail {
        background-color: #FEE2E2;
        color: #991B1B;
    }
    .why-section {
        background-color: #EFF6FF;
        border: 1px solid #BFDBFE;
        padding: 1.25rem;
        border-radius: 0.5rem;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# 侧边栏输入
st.sidebar.header("📊 请输入您的财务数据")
st.sidebar.markdown("---")

# 基础收入与支出
st.sidebar.subheader("1. 现金流数据")
monthly_income = st.sidebar.number_input("每月税后总收入 (元)", min_value=1.0, value=15000.0, step=500.0)
monthly_expense = st.sidebar.number_input("每月基本总开销 (元)", min_value=1.0, value=10000.0, step=500.0)
monthly_savings = st.sidebar.number_input("每月实际固定储蓄 (元)", min_value=0.0, value=3000.0, step=100.0)

# 资产数据
st.sidebar.subheader("2. 资产配置")
liquid_assets = st.sidebar.number_input("流动资产 (现金/活期/余额宝等，元)", min_value=0.0, value=15000.0, step=1000.0)
earning_assets = st.sidebar.number_input("生息资产 (股票/基金/国债/收租房等，元)", min_value=0.0, value=20000.0, step=1000.0)
depreciating_assets = st.sidebar.number_input("其他资产/耗钱资产 (奢侈品/衣服/车等，元)", min_value=0.0, value=30000.0, step=1000.0)

total_assets = liquid_assets + earning_assets + depreciating_assets

# 债务数据
st.sidebar.subheader("3. 债务状况")
monthly_debt = st.sidebar.number_input("每月硬性债务还款 (房贷/车贷/分期等，元)", min_value=0.0, value=4000.0, step=500.0)

# 用户背景选择
st.sidebar.subheader("4. 您的职业特征")
occupation_type = st.sidebar.selectbox(
    "选择您的职业状态",
    ["国企/事业单位/公务员 (极稳定)", "普通企业员工 (相对稳定)", "创业者/自由职业者/收入波动大"]
)

# 页面头部
st.markdown('<div class="main-title">💰 家庭财务健康深度诊断系统</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">基于董小姐《100天赚钱计划·金钱世界观》核心理论设计</div>', unsafe_allow_html=True)

# 理论前言介绍
with st.expander("📖 为什么要进行财务体检？（金钱世界观基础）", expanded=False):
    st.markdown("""
    很多人努力工作、疯狂加班，在**“一维斜杠（拼时间与精力重复劳动）”**上用体力硬扛，却发现依然存不下钱。
    要想跨越财富鸿沟，就必须通过**“升级消费观”**阻断消费主义对我们本金的蚕食，并打造成熟的**“安全试错空间”**，
    逐步把低效的劣质本金转变成**“优质生息资产”**（如核心房产、优质股债等），让资本作为外挂替我们工作。
    
    而在出发进入金融市场之前，**“知己之笔，财务诊断”是我们的第一步**。定期体检能让我们清晰亮化自己的财务防线，避免在风浪来临时陷入“断崖式下跌”的窘境。
    """)

# 计算指标
# 1. 应急能力
emergency_ratio = liquid_assets / monthly_expense if monthly_expense > 0 else 99.0
# 2. 储蓄力
savings_ratio = (monthly_savings / monthly_income) * 100 if monthly_income > 0 else 0.0
# 3. 财务负担比率
debt_ratio = (monthly_debt / monthly_income) * 100 if monthly_income > 0 else 0.0
# 4. 生息资产比例
earning_ratio = (earning_assets / total_assets) * 100 if total_assets > 0 else 0.0

# 判定逻辑与标准
# 应急标准判定
if occupation_type == "国企/事业单位/公务员 (极稳定)":
    target_emergency = 3.0
    emergency_desc = "由于您工作极稳定，失业风险极低，您的防守底线指标设为 **3 个月** 即可，多余资金应尽最大效率配置到高增值资产中。"
else:
    target_emergency = 6.0
    emergency_desc = "考虑到您的工作或收入存在一定波动，或家庭开支责任较重，您的防守安全指标应设为 **6 个月**，以确保任何突发变故下生活体面不降级。"

if emergency_ratio >= target_emergency:
    emergency_status = "合格"
    emergency_badge = '<span class="status-badge badge-pass">✅ 优良</span>'
elif emergency_ratio >= (target_emergency * 0.6):
    emergency_status = "警告"
    emergency_badge = '<span class="status-badge badge-warn">⚠️ 偏低</span>'
else:
    emergency_status = "不合格"
    emergency_badge = '<span class="status-badge badge-fail">❌ 极度危险</span>'

# 储蓄力判定
if savings_ratio >= 30.0:
    savings_badge = '<span class="status-badge badge-pass">✅ 合格</span>'
    savings_status = "合格"
else:
    savings_badge = '<span class="status-badge badge-fail">❌ 不合格</span>'
    savings_status = "不合格"

# 债务负担判定
if debt_ratio == 0:
    debt_badge = '<span class="status-badge badge-pass">✅ 零负债</span>'
    debt_status = "安全"
elif debt_ratio <= 35.0:
    debt_badge = '<span class="status-badge badge-pass">✅ 安全合理</span>'
    debt_status = "安全"
else:
    debt_badge = '<span class="status-badge badge-fail">❌ 负担沉重</span>'
    debt_status = "高危"

# 生息资产比例判定
if earning_ratio >= 50.0:
    earning_badge = '<span class="status-badge badge-pass">✅ 合格</span>'
    earning_status = "合格"
else:
    earning_badge = '<span class="status-badge badge-warn">⚠️ 偏低</span>'
    earning_status = "不合格"


# 页面主体：左右分栏
col_metrics, col_radar = st.columns([2, 1])

with col_metrics:
    st.subheader("📋 您的财务体检报告")
    
    # 1. 应急能力卡片
    st.markdown(f"""
    <div class="metric-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span class="metric-title">【指标一】 应急能力 (流动资产 / 月基本支出)</span>
            {emergency_badge}
        </div>
        <div class="metric-value">当前可支撑：{emergency_ratio:.2f} 个月 <span style="font-size:1rem; color:#6B7280;">(目标: {target_emergency} 个月)</span></div>
        <div class="why-section">
            <strong>🔍 为什么测算这项指标？</strong><br>
            应急能力是家庭财务的<b>“防撞安全气囊”</b>。它不负责生钱，但负责在您突然遭遇失业、家庭变故或收入中断时，给您和家庭提供最基本的尊严保障，避免生活水准断崖式下跌。它决定了您在遭遇糟糕环境时是否有底气“插着金钱的翅膀飞走”。
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 根据结果给出针对性建议并解释“为什么”
    st.markdown("💡 **应急建议与方案深剖：**")
    st.markdown(emergency_desc)
    if emergency_status == "不合格":
        st.error("""
        **🚨 诊断红线警报：** 您的紧急储备金严重不足！
        - **建议方案：** 立即停止非必要的大额日常开支（如买包、衣服、潮牌）。执行“有钱花钱包”扣留计划，在接下来的 3~6 个月内，发完工资后，强行将收入的 1/3 到 1/2 存入流动活期或余额宝，**直到应急备用金能完全覆盖您生活开支的目标月份数为止**。
        - **为什么这么建议？** 如果没有这层缓冲，一旦遭遇突发开支（如家人住院、孩子急需开支、工作调整），您将瞬间面临债务断裂的危险，甚至被迫在市场低点“割肉”卖出长期股票或基金等投资，造成永久性本金亏损。
        """)
    else:
        st.success("🎉 **安全防线稳固：** 您的应急流动资金充足，能够抵御大部分突发生活风险。保持当前状态，多余本金可以大胆向生息资产配置！")
        
    st.markdown("---")

    # 2. 储蓄力卡片
    st.markdown(f"""
    <div class="metric-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span class="metric-title">【指标二】 储蓄力 (月实际储蓄 / 月收入)</span>
            {savings_badge}
        </div>
        <div class="metric-value">当前储蓄率：{savings_ratio:.1f}% <span style="font-size:1rem; color:#6B7280;">(及格线: 30%)</span></div>
        <div class="why-section">
            <strong>🔍 为什么测算这项指标？</strong><br>
            储蓄力决定了您财富雪球的原始积累速度。如果每月攒不下钱，即使投资收益率再高（比如年化 20%），在极小的本金基数下也毫无意义。储蓄力是您财富大厦的地基。
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("💡 **储蓄力建议与方案深剖：**")
    if savings_status == "不合格":
        st.warning("""
        **⚠️ 诊断黄线警告：** 您的储蓄力不达标，极易陷入像“小金金”一样工作三年无存款、钱一发就光（如大姨妈般来一次一星期就没）的尴尬死循环。
        
        **🛠️ 董小姐实操降维解药：**
        1. **重塑“花钱肉痛感”：** 立即开启记账！在电子移动支付盛行的当下，刷卡让人对“本金流失”麻木，记账能重新唤醒付现金时的生理“疼惜感”，逼你审视每笔支出的必要性。
        2. **严格执行【三个钱包分配法】：**
           - **投资钱包 (钱生钱钱包) 占 1/3**：发工资第一天强行划走，雷打不动拿去定投或存起，这是你用来买“生生不息的蛋”的本金。
           - **有钱花钱包占 1/3**：覆盖衣食住行、水电房贷等硬性生存开销。
           - **爱怎么花就怎么花钱包占 1/5**：只作为小目标达成的自我奖励（如一束花、一顿大餐），确保生活质量不窒息，告别报复性消费。
        3. **24小时冷静期：** 看到昂贵的非必需品（如大牌包、潮牌），在购物车里先锁 24 小时。科学表明，90% 的消费冲动会在一天后烟消云散。
        
        **🔍 为什么这么建议？** 
        消费主义的狡猾在于让你产生“买了这个包/车，我就能成为完美形象”的幻觉，用消费定义自己。但真相是，你消费了什么，无法定义你；你<b>创造的</b>才真正代表你自己。先买鸡吃，吃完就得被迫继续卖命打工，无限轮回；先存蛋孵鸡，孵出养鸡场，未来才能有无穷无尽的鸡吃。
        """)
    else:
        st.success("🎉 **财富增殖地基牢固：** 您的储蓄习惯良好！请继续保持三个钱包的科学分流，坚决将每月积累下来的闲钱转入优质生息资产。")

    st.markdown("---")

    # 3. 财务负担比率卡片
    st.markdown(f"""
    <div class="metric-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span class="metric-title">【指标三】 财务负担比率 (每月债务还款 / 可支配月收入)</span>
            {debt_badge}
        </div>
        <div class="metric-value">当前债务占比：{debt_ratio:.1f}% <span style="font-size:1rem; color:#6B7280;">(安全红线: 35%)</span></div>
        <div class="why-section">
            <strong>🔍 为什么测算这项指标？</strong><br>
            债务是刚性流出的毒药。如果债务还款过高，将严重挤压日常生活的腾挪空间，逼迫您为了保住工作还房贷，而在职场上不敢说“不”、不敢辞职换赛道，彻底丧失说走就走的自由。
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("💡 **债务负担建议与方案深剖：**")
    if debt_status == "高危":
        st.error(f"""
        **🚨 诊断债务警报：** 您的月供负债占比 ({debt_ratio:.1f}%) 已经远远超过了 35% 的安全警戒线！
        - **建议方案：** 
          1. 绝对不能再新增任何消费贷、信用卡分期！
          2. 如果有置换大房、换豪车的计划，立即叫停。
          3. 在未来的财务计划中，优先利用年终奖或闲置贬值资产变现，偿还部分高息债务，强行把债务比率拉回 35% 以下。
        - **为什么这么建议？** 当月负债占比超过 50% 时，家庭基本没有任何容错空间（如同董小姐那位年入百万却因买学区大房每月还款 40% 的朋友）。一旦有一方遭遇降薪、失业或者老人生病，家庭信用将面临瞬间崩塌，不得不节衣缩食，严重摧残家庭幸福感。
        """)
    else:
        st.success("🎉 **负债状态极佳：** 您的负债水平处于绝对安全的安全区间或零负债状态，财务姿态极其轻盈！如果未来有购房等硬性加杠杆行为，请严格将其限制在月可支配收入的 35% 以内。")

    st.markdown("---")

    # 4. 生息资产比例卡片
    st.markdown(f"""
    <div class="metric-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span class="metric-title">【指标四】 生息资产比例 (生息资产 / 总资产)</span>
            {earning_badge}
        </div>
        <div class="metric-value">当前生息占比：{earning_ratio:.1f}% <span style="font-size:1rem; color:#6B7280;">(合格线: 50%)</span></div>
        <div class="why-section">
            <strong>🔍 为什么测算这项指标？</strong><br>
            生息资产比例决定了您<b>“让钱给您打工”</b>的真实工作效率。如果该比例过低，说明您的大量资产沉淀在无收益的死钱（如零利息活期存款）或快速贬值的奢侈品消费品（如包包、衣服、豪车等耗钱资产）中。
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("💡 **资产增值建议与方案深剖：**")
    if earning_status == "不合格":
        st.warning(f"""
        **⚠️ 诊断资产警告：** 您的生息资产占比仅有 {earning_ratio:.1f}%，未达到 50% 的合格标准，这说明您目前无法有效抵御真实的通货膨胀！
        
        **🛠️ 董小姐资产重组药方：**
        1. **看清通胀掠夺：** 躺在银行 1.5% 定期或余额宝 2% 里的存款，看似安全，但实际上在每年约 **10% 真实通胀率（广义货币M2增速）** 面前，正在以每年近 10% 的速度被“小偷”无形地割韭菜吞噬。
        2. **停止囤积折上折资产：** 不要再囤奢侈品包包、衣服等！大牌包背出柜台那一刻，二手市场直接打折，最惨打到 3 折，持有它无异于持有一款“折上折”的急速贬值资产。
        3. **打造【安全试错空间】跨出投资第一步：**
           - **选择正规场所**：只去正规银行、证券交易所或天弘基金，绝对不要碰不透明、没有国家金融监管的非正规理财平台（如曾暴雷的 P2P）。
           - **极小本金试错**：用“哪怕丢了也完全不心痛”的金额（如 1000 元或 2000 元）买入优质股票、基金等凭证。
           - **死守 20%~30% 止损点**：一旦买入的基金跌到 30% 清盘线，果断割肉离场，交学费认错。这不仅是保本手段，更是训练直面亏损、截断风险的投资心智。
           
        **🔍 为什么这么建议？**
        投资理财和学游泳一样，只在陆地上看书是学不会的。唯有用一小笔钱“真枪实弹”地投入正规市场中，经历一轮小幅度的市场波动，磨砺半年以上建立好“车感”，您才能真正将劣质资产升级成核心地段房产、优质企业股权等能跑赢通胀的优良生息资产，安全踏入 ESBI 的 <b>I (Investor 投资人)</b> 象限。
        """)
    else:
        st.success("🎉 **财务引擎运转良好：** 您的生息资产过半，正在让资金高效地参与社会造富协作。请继续坚持“做懂行投资，不碰PPT虚无概念公司”的投资常识！")


with col_radar:
    st.subheader("🎯 资产健康度雷达简析")
    
    # 模拟数据雷达，使用 Streamlit 的简单 chart
    chart_data = pd.DataFrame({
        "指标": ["应急能力", "储蓄力", "债务健康", "生息占比"],
        "您的得分": [
            min(100.0, (emergency_ratio / target_emergency) * 100),
            min(100.0, (savings_ratio / 30.0) * 100),
            min(100.0, (100.0 - (debt_ratio / 35.0) * 100) if debt_ratio <= 100.0 else 0),
            min(100.0, (earning_ratio / 50.0) * 100)
        ]
    })
    
    st.dataframe(
        chart_data.set_index("指标"),
        use_container_width=True
    )
    
    st.markdown("📌 *说明：得分达到 100 说明已安全越过董小姐设定的理财及格线。*")
    
    # 诊断总评语
    st.markdown("---")
    st.subheader("🏆 诊断终极评语")
    
    score_count = sum([emergency_status == "合格", savings_status == "合格", debt_status == "安全", earning_status == "合格"])
    if score_count == 4:
        st.balloons()
        st.success("🏆 **财务王者（神雕侠侣型）：** 您的四项财务指标全部合格！您已经拥有了扎实健全的金钱世界观，防线稳固，大厦牢固，非常适合向 Level 1（实战科目二：踩离合、挂档）实操投资进发！")
    elif score_count >= 2:
        st.info("📈 **财务稳健（中规中矩型）：** 您的财务地基基本合格，但仍有 1~2 处防御漏洞容易遭到通货膨胀或消费主义的侵袭。请针对黄色/红色警报指标，按上面开出的药方迅速调整钱包比例。")
    else:
        st.error("🚨 **财务高危（小金金同款）：** 您的家庭财务漏洞极其严重，几乎是在无防线、无蓄水、重债务或劣质资产积压的状态下在生活的风雨中裸奔。请立刻执行记账、冻结非必要大额开支，死守‘三个钱包’强行重组本金结构！")

