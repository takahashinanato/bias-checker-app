import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# .envからAPIキーを読み込む
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# 診断履歴カウント（1人5回まで）
if "diagnosis_count" not in st.session_state:
    st.session_state.diagnosis_count = 0

st.title("🧠 政治的バイアス診断アプリ")
st.markdown("SNS投稿や自身の意見などから政治的意見を入力してください（100字以内）。例：『憲法改正は必要だと思う』『夫婦別姓制度は導入されるべきだ』")

user_input = st.text_area("投稿内容", key="user_input")

# ボタン押下時
if st.button("診断する", key="diagnose_button") and user_input:
    if st.session_state.diagnosis_count >= 5:
        st.warning("プロトタイプでは1人5回までの診断に制限されています。")
    else:
        prompt = f"""
以下のSNS投稿から、以下の3つを出力してください：

1. 政治的傾向スコア（-1.0=保守、+1.0=リベラル）
2. バイアス強度スコア（0.0〜1.0）
3. コメント（なぜそのスコアになったか、該当箇所を指摘して事実ベースでハルシネーションを起こさないようになるべく中立的に200文字程度で）

投稿内容: {user_input}

出力フォーマット:
傾向（リベラル的か保守的か）スコア: 数値
強さ（意見の過激度）スコア: 数値
コメント: ○○○○（理由）
"""

        with st.spinner("診断中..."):
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            result = response.choices[0].message.content

        st.session_state.diagnosis_count += 1
        st.success("診断結果")

        try:
            lines = result.strip().split("\n")
            bias_score = float(lines[0].split(":")[1].strip())
            strength_score = float(lines[1].split(":")[1].strip())
            comment = lines[2].split(":", 1)[1].strip()

            st.markdown(f"**傾向スコア:** {bias_score}　　**強さスコア:** {strength_score}")
            st.markdown(f"**コメント:** {comment}")

            # フォント設定（Streamlit Cloud用にフォントファイル読み込み）
            font_path = "./fonts/NotoSansCJKjp-Regular.otf"
            if os.path.exists(font_path):
                font_prop = fm.FontProperties(fname=font_path)
                plt.rcParams["font.family"] = font_prop.get_name()
                st.write("フォント読み込み成功:", font_prop.get_name())
            else:
                st.warning("フォントファイルが見つかりません。")

            fig, ax = plt.subplots()
            ax.scatter(bias_score, strength_score, color="blue")
            ax.set_xlim(-1.0, 1.0)
            ax.set_ylim(0.0, 1.0)
            ax.set_xlabel("政治的傾向スコア（-1.0 = 保守　+1.0 = リベラル）")
            ax.set_ylabel("表現の強さスコア（0.0〜1.0）")
            ax.grid(True)

            # 軸の外にラベルを追加
            ax.text(-1.0, -0.05, "保守", ha="center", va="top", fontsize=9, fontproperties=font_prop)
            ax.text(1.0, -0.05, "リベラル", ha="center", va="top", fontsize=9, fontproperties=font_prop)
            ax.text(0.05, 0.0, "過激", ha="left", va="bottom", fontsize=9, fontproperties=font_prop)
            ax.text(0.05, 1.0, "穏健", ha="left", va="top", fontsize=9, fontproperties=font_prop)

            st.pyplot(fig)

        except Exception as e:
            st.error("診断結果の解析に失敗しました。フォーマットを確認してください。")

# 診断回数表示
st.info(f"診断回数：{st.session_state.diagnosis_count}/5")
