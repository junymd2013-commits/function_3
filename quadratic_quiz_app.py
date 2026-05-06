import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import random

st.set_page_config(page_title="二次関数4択クイズ", layout="centered")

# セッション状態の初期化
if "a_list" not in st.session_state:
    st.session_state.a_list = None
    st.session_state.b_list = None
    st.session_state.c_list = None
    st.session_state.correct_index = None
    st.session_state.answered = False
    st.session_state.message = ""
    st.session_state.finished = False

def generate_quadratic_choices():
    # 正解の二次関数をランダム生成
    a = random.choice([-3, -2, -1, 1, 2, 3])
    b = random.randint(-5, 5)
    c = random.randint(-5, 5)

    a_list = [a]
    b_list = [b]
    c_list = [c]

    # 誤答3つを生成（形は似ているが少しずつ違う）
    while len(a_list) < 4:
        mode = random.choice(["a", "b", "c"])
        if mode == "a":
            a2 = a + random.choice([-2, -1, 1, 2])
            b2, c2 = b, c
        elif mode == "b":
            a2 = a
            b2 = b + random.choice([-3, -2, -1, 1, 2, 3])
            c2 = c
        else:
            a2 = a
            b2 = b
            c2 = c + random.choice([-3, -2, -1, 1, 2, 3])

        # 完全重複は避ける
        if (a2, b2, c2) not in zip(a_list, b_list, c_list):
            a_list.append(a2)
            b_list.append(b2)
            c_list.append(c2)

    # 選択肢をシャッフル
    indices = list(range(4))
    random.shuffle(indices)
    a_list = [a_list[i] for i in indices]
    b_list = [b_list[i] for i in indices]
    c_list = [c_list[i] for i in indices]

    # 正解の位置（元の正解は index 0 だった）
    correct_index = indices.index(0)

    return a_list, b_list, c_list, correct_index

def new_question():
    st.session_state.a_list, st.session_state.b_list, st.session_state.c_list, st.session_state.correct_index = generate_quadratic_choices()
    st.session_state.answered = False
    st.session_state.message = ""
    st.session_state.finished = False

# 最初の問題生成
if st.session_state.a_list is None:
    new_question()

st.title("二次関数：グラフ4択問題")

st.write("1つの座標平面上に、4つの二次関数のグラフが描かれています。")
st.write("正しいグラフを1つ選んでください。")

# グラフ描画
x = np.linspace(-10, 10, 400)
fig, ax = plt.subplots(figsize=(6, 6))

colors = ["tab:blue", "tab:orange", "tab:green", "tab:red"]

for i in range(4):
    a = st.session_state.a_list[i]
    b = st.session_state.b_list[i]
    c = st.session_state.c_list[i]
    y = a * x**2 + b * x + c
    ax.plot(x, y, color=colors[i], label=f"選択肢{i+1}")

ax.axhline(0, color="black", linewidth=1)
ax.axvline(0, color="black", linewidth=1)
ax.set_xlim(-10, 10)
ax.set_ylim(-10, 10)
ax.grid(True)
ax.legend(loc="upper left")

st.pyplot(fig)

# 選択肢
choice = st.radio(
    "正しいと思うグラフを選んでください。",
    options=[1, 2, 3, 4],
    format_func=lambda x: f"選択肢{x}",
    horizontal=True
)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("答え合わせ"):
        if not st.session_state.answered:
            st.session_state.answered = True
            if choice - 1 == st.session_state.correct_index:
                st.session_state.message = "✅ 正解です！"
            else:
                st.session_state.message = f"❌ 不正解です。正解は「選択肢{st.session_state.correct_index+1}」でした。"

with col2:
    if st.button("次の問題"):
        new_question()

with col3:
    if st.button("終了"):
        st.session_state.finished = True
        st.session_state.message = "お疲れさまでした。これで終了です。"

if st.session_state.message:
    st.write(st.session_state.message)

if st.session_state.finished:
    st.stop()
