import streamlit as st
import pandas as pd
from io import BytesIO
import altair as alt
import os
from datetime import datetime
from PIL import Image

FILE = "qr_data.xlsx"
LOG_FILE = "scans_log.xlsx"

# Inicializa arquivos
if not os.path.exists(FILE):
    df = pd.DataFrame([{"ID": 1, "URL": "", "Scans": 0}])
    df.to_excel(FILE, index=False)

if not os.path.exists(LOG_FILE):
    log_df = pd.DataFrame(columns=["ID", "DataHora"])
    log_df.to_excel(LOG_FILE, index=False)

st.set_page_config(page_title="Luadeira Digital", page_icon="📊", layout="wide")

# --- Credenciais fixas ---
ADMIN_USER = "admin"
ADMIN_PASS = "1234"

# --- Processa leitura pública ---
qr_id = st.query_params.get("qr_id", None)
if qr_id:
    qr_id = int(qr_id[0])
    df = pd.read_excel(FILE)
    log_df = pd.read_excel(LOG_FILE)

    # Corrige dados
    if "Scans" not in df.columns or df.empty:
        df = pd.DataFrame([{"ID": 1, "URL": "", "Scans": 0}])
        df.to_excel(FILE, index=False)

    df["Scans"] = df["Scans"].fillna(0).astype(int)

    if qr_id == 1:
        df.loc[0, "Scans"] += 1
        df.to_excel(FILE, index=False)

        # Registra log
        new_log = pd.DataFrame([{"ID": 1, "DataHora": datetime.now()}])
        log_df = pd.concat([log_df, new_log], ignore_index=True)
        log_df.to_excel(LOG_FILE, index=False)

        url = df.loc[0, "URL"]
        st.success("📲 QR lido! Redirecionando...")
        st.markdown(f'<meta http-equiv="refresh" content="0; url={url}">', unsafe_allow_html=True)
    else:
        st.error("⚠️ QR inválido.")
    st.stop()

# --- Sidebar login ---
with st.sidebar:
    st.markdown("### 🔑 Área Administrativa")
    if "role" not in st.session_state:
        st.session_state.role = "guest"

    if st.session_state.role != "admin":
        username = st.text_input("Usuário", key="user_sidebar")
        password = st.text_input("Senha", type="password", key="pass_sidebar")
        if st.button("Entrar", key="login_btn"):
            if username == ADMIN_USER and password == ADMIN_PASS:
                st.session_state.role = "admin"
                st.success("✅ Login realizado!")
                st.rerun()
            else:
                st.error("❌ Usuário ou senha incorretos.")
    else:
        st.success("✅ Logado como administrador")
        if st.button("Sair", key="logout_btn"):
            st.session_state.role = "guest"
            st.rerun()

# --- Página inicial (antes do login) ---
if st.session_state.role != "admin":
    if os.path.exists("logo.png"):
        st.image("logo.png", width=200)
    st.title("✨ Bem-vindo à Luadeira Digital ✨")
    st.markdown(
        """
        **Acreditamos no poder dos eventos para transformar experiências.**  
        Cada encontro é uma oportunidade de criar conexões, inspirar pessoas e fortalecer a cultura.  
        Com tecnologia e inovação, a **Luadeira Digital** ajuda você a realizar eventos inesquecíveis. 🎉  
        """
    )
    st.info("Faça login no menu lateral para acessar estatísticas de leituras.")
    st.stop()

# --- Estatísticas do Admin ---
st.success("✅ Bem-vindo, administrador!")

df = pd.read_excel(FILE)
log_df = pd.read_excel(LOG_FILE)

# Corrige possíveis inconsistências
if "Scans" not in df.columns or df.empty:
    df = pd.DataFrame([{"ID": 1, "URL": "", "Scans": 0}])
    df.to_excel(FILE, index=False)

df["Scans"] = df["Scans"].fillna(0).astype(int)

scans = int(df.loc[0, "Scans"])
url = df.loc[0, "URL"]

col1, col2 = st.columns(2)
col1.metric("🔗 QR Criado", "1")
col2.metric("📲 Total de Scans", scans)

# 📊 Gráficos em abas
st.subheader("📊 Estatísticas de Leitura")

if not log_df.empty:
    log_df["DataHora"] = pd.to_datetime(log_df["DataHora"], errors="coerce")

    tab1, tab2, tab3 = st.tabs(["📅 Por Dia", "⏰ Por Hora", "🗓️ Por Mês"])

    with tab1:
        scans_por_dia = log_df.groupby(log_df["DataHora"].dt.date).size().reset_index(name="Scans")
        chart_dia = alt.Chart(scans_por_dia).mark_bar(color="#4E79A7").encode(
            x=alt.X("DataHora:T", title="Dia"),
            y=alt.Y("Scans:Q", title="Total de Scans"),
            tooltip=["DataHora", "Scans"]
        ).properties(title="📅 Scans por Dia", width=700, height=300)
        st.altair_chart(chart_dia, use_container_width=True)

    with tab2:
        scans_por_hora = log_df.groupby(log_df["DataHora"].dt.hour).size().reset_index(name="Scans")
        chart_hora = alt.Chart(scans_por_hora).mark_bar(color="#F28E2B").encode(
            x=alt.X("DataHora:O", title="Hora do Dia"),
            y=alt.Y("Scans:Q", title="Total de Scans"),
            tooltip=["DataHora", "Scans"]
        ).properties(title="⏰ Scans por Hora", width=700, height=300)
        st.altair_chart(chart_hora, use_container_width=True)

    with tab3:
        scans_por_mes = log_df.groupby(log_df["DataHora"].dt.to_period("M")).size().reset_index(name="Scans")
        scans_por_mes["DataHora"] = scans_por_mes["DataHora"].astype(str)
        chart_mes = alt.Chart(scans_por_mes).mark_bar(color="#59A14F").encode(
            x=alt.X("DataHora:O", title="Mês"),
            y=alt.Y("Scans:Q", title="Total de Scans"),
            tooltip=["DataHora", "Scans"]
        ).properties(title="🗓️ Scans por Mês", width=700, height=300)
        st.altair_chart(chart_mes, use_container_width=True)

else:
    st.info("Ainda não há leituras registradas para gerar gráficos.")

# 📋 Histórico
st.subheader("📋 Histórico de Leituras")
if not log_df.empty:
    st.dataframe(log_df, use_container_width=True)
else:
    st.info("Ainda não há leituras registradas.")

# 📤 Exportar Excel
excel_buffer = BytesIO()
with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
    df.to_excel(writer, index=False, sheet_name="Resumo")
    log_df.to_excel(writer, index=False, sheet_name="Historico")
st.download_button("⬇️ Exportar estatísticas em Excel",
                   data=excel_buffer,
                   file_name="qr_code_stats.xlsx",
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ⚙️ Ações administrativas
st.subheader("⚙️ Ações Administrativas")
col1, col2 = st.columns(2)

if col1.button("🧹 Zerar contagem (somente total)"):
    df.loc[0, "Scans"] = 0
    df.to_excel(FILE, index=False)
    st.success("✅ Contagem de leituras zerada (histórico preservado)!")
    st.rerun()

if col2.button("🗑️ Apagar todo histórico de scans"):
    log_df = pd.DataFrame(columns=["ID", "DataHora"])
    log_df.to_excel(LOG_FILE, index=False)
    st.success("✅ Histórico de leituras apagado!")
    st.rerun()
