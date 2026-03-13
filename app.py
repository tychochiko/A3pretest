import streamlit as st
import csv
import os
import random
import datetime
import uuid
from zhipuai import ZhipuAI

# =========================
# API 设置
# =========================

client = ZhipuAI(api_key=os.getenv("ZHIPUAI_API_KEY"))
MODEL = "glm-4.5-air"

def generate_next_kudos(previous_text, next_name):

    system_prompt = """
你是一名医院宣传部工作者。
你的任务是为表现优秀的护士撰写简短的内部表彰文字。
每条表彰信息约为80-120字。 
"""

    user_prompt = f"""
以下是上一条已完成的表彰内容示例：

{previous_text}

请为下一位优秀护士{next_name}撰写一条新的表彰信息。
"""

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        top_p=0.9,
    )

    return resp.choices[0].message.content.strip()


# =========================
# 页面标题
# =========================

st.title("医院内部表彰信息编辑系统")


# =========================
# 初始化
# =========================

if "condition" not in st.session_state:
    st.session_state.condition = random.choice(["stereotype", "counter"])

if "round" not in st.session_state:
    st.session_state.round = 1

if "stage" not in st.session_state:
    st.session_state.stage = "consent"

if "participant_id" not in st.session_state:
    st.session_state.participant_id = "P_" + str(uuid.uuid4())[:8]

if "confirm_no_change" not in st.session_state:
    st.session_state.confirm_no_change = False

if "current_text" not in st.session_state:
    st.session_state.current_text = ""


# =========================
# 操纵文本
# =========================

if st.session_state.condition == "stereotype":
    first_text = (
        "特别表扬护士赵宁。"
        "她性格温和细致，在日常护理中总是微笑甜美，耐心倾听并回应患者的需求，给予安慰与陪伴。"
        "无论是夜班还是繁忙时段，她都像一位母亲一样，以温暖的关怀让患者感到安心与信任，是备受喜爱的贴心姐姐。"
    )
else:
    first_text = (
        "特别表扬护士赵宁。"
        "赵宁业务能力扎实，熟练掌握各项临床操作流程，在突发情况中能够迅速判断并准确执行处置方案。"
        "赵宁注重规范管理与团队协作，多次在复杂病例处理中发挥关键作用，是科室稳定运行的重要力量。"
    )

names = ["赵宁", "李晨", "刘嘉宁", "郑昕", "许书涵", "黄安然"]

current_round = st.session_state.round


# =========================
# 实验结束
# =========================

if current_round > 6:

    # 第一步：显示参与编号页面
    if "id_confirmed" not in st.session_state:
        st.session_state.id_confirmed = False

    if not st.session_state.id_confirmed:

        st.write("您已经完成了改写任务。")

        st.write("您的参与编号如下，请复制该编号并在问卷中填写：")

        st.markdown(
            f"""
            <div style="
                font-size:18px;
                font-weight:bold;
                margin:10px 0;">
            {st.session_state.participant_id}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("请复制编号后，点击下方按钮继续。")

        if st.button("我已复制编号"):
            st.session_state.id_confirmed = True
            st.rerun()

        st.stop()

    # 第二步：感谢语 + 问卷链接
    else:

        st.write("感谢您的参与。请点击下方链接完成后续问卷。")

        survey_link = "https://wj.qq.com/s2/25959280/5910/"

        st.markdown(f"[点击进入问卷填写]({survey_link})")

        st.stop()

# =========================
# Consent 页面
# =========================

if st.session_state.stage == "consent":

    st.markdown(
        """
        <div style="line-height:1.5; font-size:16px;">

        <p>欢迎参与本次在线任务。本任务围绕测试中的人工智能（AI）生成系统展开，您将以医院宣传负责人的身份，对AI生成的内部表彰初稿进行审核与修改。</p>

        <p>整个过程约需8–10分钟。任务不涉及任何风险或敏感内容。所有数据将匿名记录，仅用于研究分析。</p>

        <p>您可以在任何时间退出任务，退出不会产生任何不良影响。</p>

        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("我已阅读并同意参与"):
        st.session_state.stage = "intro"
        st.rerun()

    st.stop()

# =========================
# Intro 页面
# =========================

if st.session_state.stage == "intro":

    st.markdown(
        """
        <div style="line-height:1.5; font-size:16px;">

        <p>欢迎参加本次AI编辑测试。</p>

        <p>医院使用AI系统自动生成优秀护士的内部表彰初稿。您的任务是修改和审核表彰初稿，并确认最终版本。</p>

        <p><strong>您的角色：</strong>医院宣传负责人；<strong>您的任务：</strong>审核并修改AI生成的表彰内容，确保其表达得当。</p>

        </div>
        """,
        unsafe_allow_html=True
    )
    
    if st.button("开始"):
        st.session_state.stage = "exposure"
        st.rerun()


# =========================
# 第一轮 exposure
# =========================

elif current_round == 1 and st.session_state.stage == "exposure":

    st.session_state.current_text = first_text

    st.write("请仔细阅读以下AI生成的表彰内容案例。")

    st.markdown(
        f"""
        <div style="
            font-size:16px;
            color:#555555;
            font-style:italic;
            line-height:1.6;
            margin-bottom:12px;">
        {st.session_state.current_text}
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("我已阅读，继续"):
        st.session_state.stage = "edit"
        st.rerun()


# =========================
# 编辑阶段（所有轮次）
# =========================

else:

    original_text = st.session_state.current_text

    st.write("请审核并修改以下表彰内容")

    st.markdown(
        f"""
        <div style="
            font-size:14px;
            color:#555555;
            font-style:italic;
            line-height:1.6;
            margin-bottom:12px;">
        {original_text}
        </div>
        """,
        unsafe_allow_html=True
    )

    edited_text = st.text_area(
        label="您可以对内容进行修改、补充或删减。",
        value=original_text,
        height=180
    )

    if st.button("确认并继续"):

        if edited_text.strip() == "":
            st.warning("内容不能为空，请审核或修改表彰文本。")
            st.stop()

        if edited_text.strip() == original_text.strip() and not st.session_state.confirm_no_change:
            st.session_state.confirm_no_change = True
            st.warning(
                "您尚未对内容进行修改。"
                "如果您认为当前内容已经合适，请再次点击“确认并继续”；"
                "否则，您可以对文本进行修改。"
            )
            st.stop()

        st.session_state.confirm_no_change = False

        # 准备写入
        timestamp = datetime.datetime.now().isoformat()

        if edited_text.strip() == original_text.strip():
            no_change_confirmed = 1
        else:
            no_change_confirmed = 0

        ai_text = original_text

        # 写入
        # 确保 data 文件夹存在
        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)

        # 每个参与者一个独立文件
        file_path = f"{data_dir}/{st.session_state.participant_id}.csv"

        file_exists = os.path.isfile(file_path)

        with open(file_path, mode="a", newline="", encoding="utf-8-sig") as file:

            if not file_exists:
                writer.writerow([
                    "participant_id",
                    "condition",
                    "block",
                    "ai_text",
                    "edited_text",
                    "no_change_confirmed",
                    "timestamp"])

            writer.writerow([
                st.session_state.participant_id,
                st.session_state.condition,
                current_round-1,
                ai_text,
                edited_text,
                no_change_confirmed,
                timestamp
            ])

        if current_round < 6:

            next_name = names[current_round]

            with st.spinner("AI正在生成下一条表彰内容..."):
                new_text = generate_next_kudos(edited_text, next_name)

            st.session_state.current_text = new_text

        st.session_state.round += 1
        st.rerun()
