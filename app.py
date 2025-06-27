import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# ✅ 日本語フォントを設定（Windowsなら「メイリオ」）
matplotlib.rcParams['font.family'] = 'sans-serif'

# ✅ APIキーを読み込む（.envファイルを使う）
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# ✅ 診断回数を記録（最大5回まで）
if "diagnosis_count" not in st.session_state:
    st.session_state.diagnosis_count = 0

# ✅ タイトルと説明
st.title("🧠 政治バイアス検出ツール")
st.markdown("SNS投稿や自身の意見など政治に関連することを200字以内で入力してください。（例：「憲法改正は必要だと思う」「夫婦別姓制度は導入されるべき」）")

# ✅ ユーザー入力欄
user_input = st.text_area("投稿内容", key="user_input")

# ✅ 診断ボタン
if st.button("診断する") and user_input:
    if st.session_state.diagnosis_count >= 5:
        st.warning("このプロトタイプでは、1人あたり最大5回まで診断できます。")
    else:
        # GPTに渡すプロンプト
        prompt = f"""
以下のSNS投稿から、以下の3つを出力してください：

1. 政治的傾向スコア（-1.0=保守、+1.0=リベラル）
2. バイアス強度スコア（0.0〜1.0）
3. コメント（なぜそのスコアになったか該当箇所を指摘しながら、可能な限り中立的に述べてください。そして絶対に事実ベースで評価してください。保守的とリベラル的をよく精査してください。200文字以内で）

投稿内容: {user_input}

出力フォーマット:
傾向（リベラル的か保守的か）スコア: 数値
強さ（意見の過激度）スコア: 数値
コメント: ○○○○
"""

        # ✅ GPTへ診断依頼
        with st.spinner("診断中..."):
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            result = response.choices[0].message.content

        # ✅ 診断回数を更新
        st.session_state.diagnosis_count += 1
        st.success("診断結果")

        # ✅ 結果の解析と可視化
        try:
            lines = result.strip().split("\n")
            bias_score = float(lines[0].split(":")[1].strip())
            strength_score = float(lines[1].split(":")[1].strip())
            comment = lines[2].split(":", 1)[1].strip()

            st.markdown(f"**傾向スコア:** {bias_score}　　**強さスコア:** {strength_score}")
            st.markdown(f"**コメント:** {comment}")
            # 日本語フォントを明示的に読み込む（Streamlit Cloud用）
            font_path = "./fonts/NotoSansCJKjp-Regular.otf"
            font_prop = fm.FontProperties(fname=font_path)
            plt.rcParams['font.family'] = plt.rcParams['font.family'] = 'DejaVu Sans'



            fig, ax = plt.subplots()
            ax.scatter(bias_score, strength_score, color="blue")
            ax.set_xlim(-1.0, 1.0)
            ax.set_ylim(0.0, 1.0)
            ax.set_xlabel("政治的傾向スコア（-1.0 = 保守　+1.0 = リベラル）")
            ax.set_ylabel("表現の強さスコア（0.0 = 穏健　1.0 = 過激）")
            ax.grid(True)

            # ラベル追加
            ax.text(-1.0, -0.05, "保守", ha="center", va="top", fontsize=9)
            ax.text(1.0, -0.05, "リベラル", ha="center", va="top", fontsize=9)
            ax.text(0.05, 0.0, "過激", ha="left", va="bottom", fontsize=9)
            ax.text(0.05, 1.0, "穏健", ha="left", va="top", fontsize=9)

            st.pyplot(fig)

        except Exception as e:
            st.error("診断結果の解析に失敗しました。GPTの出力フォーマットを確認してください。")

# ✅ 診断回数の表示
st.info(f"診断回数：{st.session_state.diagnosis_count}/5")
