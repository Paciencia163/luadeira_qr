import streamlit as st
import pandas as pd
import os
from datetime import datetime
import altair as alt

FILE = "qr_data.xlsx"
LOG_FILE = "scans_log.xlsx"

# Inicializa arquivos se não existirem
if not os.path.exists(FILE):
    df = pd.DataFrame([{"ID": 1, "URL": "", "Scans": 0}])
    df.to_excel(FILE, index=False)

if not os.path.exists(LOG_FILE):
    log_df = pd.DataFrame(columns=["QR_ID", "DataHora"])
    log_df.to_excel(LOG_FILE, index=False)

st.set_page_config(page_title="Luadeira Digital - Evento", page_icon="🎉", layout="wide")

# --- SESSION STATE ---
if "logado" not in st.session_state:
    st.session_state["logado"] = False

# --- SIDEBAR LOGIN ---
st.sidebar.title("🔐 Área Administrativa")
usuario = st.sidebar.text_input("Usuário")
senha = st.sidebar.text_input("Senha", type="password")
if st.sidebar.button("Entrar"):
    if usuario == "admin" and senha == "1234":
        st.session_state["logado"] = True
        st.sidebar.success("✅ Logado com sucesso!")
        st.rerun()
    else:
        st.sidebar.error("❌ Credenciais inválidas")

if st.sidebar.button("Sair"):
    st.session_state["logado"] = False
    st.rerun()

# --- PÁGINA INICIAL (todos os usuários) ---
st.image("logo.png", use_container_width=True)

st.title("🎉 Bem-vindo ao Evento da **Luadeira Digital**")
st.markdown(
    """
    🌟 **Uma experiência inesquecível!**  
    Estamos felizes em recebê-lo neste grande momento de celebração, tecnologia e conexões.  
    Cada leitura do QR Code é um passo rumo a um evento mais interativo e digital.  
    Aproveite cada instante! 🚀✨
    """
)

# --- CAPTURA DO QR ---
query_params = st.query_params
qr_id = int(query_params.get("qr_id", [1])[0])  # padrão = 1

df = pd.read_excel(FILE)
log_df = pd.read_excel(LOG_FILE)

# Se não existe esse QR ainda no Excel, cria
if qr_id not in df["ID"].values:
    df = pd.concat([df, pd.DataFrame([{"ID": qr_id, "URL": "", "Scans": 0}])], ignore_index=True)
    df.to_excel(FILE, index=False)

# Normaliza coluna Scans
df["Scans"] = df["Scans"].fillna(0).astype(int)

# Incrementa leitura do QR (todos contam, mesmo sem login)
df.loc[df["ID"] == qr_id, "Scans"] += 1
df.to_excel(FILE, index=False)

# Salva log
novo_log = pd.DataFrame([{"QR_ID": qr_id, "DataHora": datetime.now()}])
log_df = pd.concat([log_df, novo_log], ignore_index=True)
log_df.to_excel(LOG_FILE, index=False)

st.success(f"✅ QR Code **{qr_id}** registrado com sucesso! Obrigado por participar! 🙌")

# --- ÁREA ADMINISTRATIVA (somente se logado) ---
if st.session_state["logado"]:
    st.markdown("---")
    st.header("📊 Estatísticas Administrativas")

    # 🔹 KPIs principais
    total_scans = int(df["Scans"].sum())
    total_qrs = df["ID"].nunique()
    scans_unicos = len(log_df["QR_ID"].unique())

    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("📌 Total de Leituras", total_scans)
    kpi2.metric("🔑 QR Codes Ativos", total_qrs)
    kpi3.metric("👥 Scans Únicos", scans_unicos)

    # 🔹 Estatísticas por QR
    st.subheader("📈 Resumo por QR Code")
    resumo = log_df.groupby("QR_ID").agg(
        Total_Leituras=("QR_ID", "count"),
        Primeira_Leitura=("DataHora", "min"),
        Ultima_Leitura=("DataHora", "max")
    ).reset_index()

    st.dataframe(resumo, use_container_width=True)

    # 🔹 Log detalhado de todas as leituras
    st.subheader("📜 Log Completo de Leituras")
    st.dataframe(log_df.tail(50), use_container_width=True)  # mostra últimas 50 entradas

    # Exportar log
    st.download_button(
        "📥 Baixar Log Completo em Excel",
        data=log_df.to_excel(index=False, engine="openpyxl"),
        file_name="log_leituras.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # 🔹 Gráficos
    st.subheader("📊 Gráficos Interativos")
    if not log_df.empty:
        log_df["DataHora"] = pd.to_datetime(log_df["DataHora"], errors="coerce")

        tabs = st.tabs(["📅 Por Dia", "⏰ Por Hora", "🗓️ Por Mês"])

        # --- Scans por Dia ---
        with tabs[0]:
            scans_por_dia = log_df.groupby(log_df["DataHora"].dt.date).size().reset_index(name="Scans")
            chart_dia = alt.Chart(scans_por_dia).mark_line(point=True, color="#4E79A7").encode(
                x=alt.X
