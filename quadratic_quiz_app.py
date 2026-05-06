import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import random
import datetime
import gspread
from google.oauth2.service_account import Credentials

st.title("二次関数：グラフ4択問題")
st.write("Secrets keys:", list(st.secrets.keys()))


# --- セッション状態の初期化 ---
if "prev_a" not in st.session_state:
    st.session_state.prev_a = None
if "answered" not in st.session_state:
    st.session_state.answered = False
if "correct_index" not in st.session_state:
    st.session_state.correct_index = None

# --- 難易度判定 ---
def get_difficulty(a):
    if abs(a) == 1:
        return "易"
    elif abs(a) == 2:
        return "普"
    else:
        return "難"

# --- Google Sheets に記録 ---
def send_to_sheet_quadratic(correct, selected, a, b, c, p, q, elapsed, difficulty):
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )

    client = gspread.authorize(creds)
    sheet = client.open_by_key(st.secrets["sheet_id"]).worksheet("二次関数_履歴")

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    row = [
        now,
        elapsed,
        difficulty,
        f"{a},{b},{c}",
        f"({p},{q})",
        correct + 1,
        selected + 1,
        "○" if correct == selected else "×"
    ]

    sheet.append_row(row)

# --- 新しい問題を作る ---
def generate_problem():
    possible_a = [-3, -2, -1, 1, 2, 3]
    if st.session_state.prev_a in possible_a:
        possible_a.remove(st.session_state.prev_a)
    a = random.choice(possible_a)

    p = random.randint(-3, 3)
    q = random.randint(-5, 5)

    st.session_state.prev_a = a

    b = -2 * a * p
    c = a * p * p + q

    return a, b, c, p, q

# --- 初回 or 次の問題 ---
if not st.session_state.answered:
    a, b, c, p, q = generate_problem()
    st.session_state.problem = (a, b, c, p, q)
    st.session_state.start_time = datetime.datetime.now()
else:
    a, b, c, p, q = st.session_state.problem

# --- 正解の関数 ---
def f(x):
    return a*x**2 + b*x + c

# --- 誤答の関数 ---
def make_wrong():
    da = random.choice([-2, -1, 1, 2])
    db = random.choice([-3, -2, -1, 1, 2, 3])
    dc = random.choice([-3, -2, -1, 1, 2, 3])
    return lambda x: (a+da)*x**2 + (b+db)*x + (c+dc)

wrong_funcs = [make_wrong() for _ in range(3)]

# --- グラフ描画 ---
x = np.linspace(-5, 5, 200)

funcs = [f] + wrong_funcs
random.shuffle(funcs)

correct_index = funcs.index(f)
st.session_state.correct_index = correct_index

figs = []
for func in funcs:
    fig, ax = plt.subplots(figsize=(3, 3))  # スマホ最適化
    ax.plot(x, func(x), linewidth=2)
    ax.axhline(0, color="black", linewidth=0.5)
    ax.axvline(0, color="black", linewidth=0.5)
    ax.set_xticks([])
    ax.set_yticks([])
    plt.tight_layout()
    figs.append(fig)

# --- 選択肢表示 ---
st.write("正しいグラフを選んでください。")

choice = st.radio(
    "選択肢",
    options=[0, 1, 2, 3],
    format_func=lambda x: f"選択肢 {x+1}"
)

for i, fig in enumerate(figs):
    st.subheader(f"選択肢 {i+1}")
    st.pyplot(fig)

# --- 回答ボタン ---
if st.button("回答する"):
    st.session_state.answered = True

    elapsed = int((datetime.datetime.now() - st.session_state.start_time).total_seconds())
    difficulty = get_difficulty(a)

    if choice == correct_index:
        st.success("正解です！")
    else:
        st.error(f"不正解です。正解は 選択肢 {correct_index+1} でした。")

    st.info(f"""
    【解説】
    y = {a}x² + {b}x + {c}
    頂点：({p}, {q})
    軸：x = {p}
    """)

    send_to_sheet_quadratic(
        correct=correct_index,
        selected=choice,
        a=a, b=b, c=c,
        p=p, q=q,
        elapsed=elapsed,
        difficulty=difficulty
    )

    if st.button("次の問題へ"):
        st.session_state.answered = False
        st.rerun()

    if st.button("終了する"):
        st.stop()
