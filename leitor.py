import streamlit as st
import pandas as pd
import os
from datetime import datetime
import altair as alt
from io import BytesIO

# Arquivos locais
LOG_FILE = "scans_log.xlsx"

# Inicializa arquivo de log
if not os.path.exists(LOG_FILE):
    log_df = pd.DataFrame(columns=["DataHora"])
    log_df.to_excel(LOG_FILE, index=False)

st.set_page_config(
    page_title="Controle de Entrada - Luadeira Digital",
    page_icon="🎟️",
    layout="wide"
)

# --- SESSION STATE ---
if "logado" not in st.session_state:
    st.session_state["logado"] = False

# --- SIDEBAR LOGIN ---
with st.sidebar:
    st.title("🔐 Área Administrativa")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if usuario == "admin" and senha == "1234":
            st.session_state["logado"] = True
            st.success("✅ Logado com sucesso!")
            st.rerun()
        else:
            st.error("❌ Credenciais inválidas")

    if st.button("Sair"):
        st.session_state["logado"] = False
        st.rerun()

# --- PÁGINA INICIAL (visível a todos) ---
st.image("logo.png", use_container_width=True)

st.title("🎉 Bem-vindo a **EXPO CATOTA**")
st.markdown(
    """
    🌟 **Um evento que conecta pessoas e experiências!**  
    Sua presença é muito importante para nós.  
    Obrigado por participar e fazer parte deste grande momento! 🚀✨
    """
)

# --- CAPTURA DO SCAN ---
query_params = st.query_params
scanned = "qr_id" in query_params  # se o QR foi lido, terá esse parâmetro

# Carregar log
log_df = pd.read_excel(LOG_FILE)

if scanned:
    # Registra entrada
    novo_log = pd.DataFrame([{"DataHora": datetime.now()}])
    log_df = pd.concat([log_df, novo_log], ignore_index=True)
    log_df.to_excel(LOG_FILE, index=False)

    st.success("✅ Presença registrada com sucesso! Bem-vindo ao evento 🙌")

# --- ÁREA ADMINISTRATIVA ---
if st.session_state["logado"]:
    st.markdown("---")
    st.header("📊 Painel Administrativo - Controle de Entrada")

    # Processar dados
    log_df["DataHora"] = pd.to_datetime(log_df["DataHora"], errors="coerce")

    total_entradas = len(log_df)
    hoje = datetime.now().date()
    entradas_hoje = len(log_df[log_df["DataHora"].dt.date == hoje])
    ultima_entrada = log_df["DataHora"].max() if not log_df.empty else "N/A"
    pico_horario = (
        log_df["DataHora"].dt.hour.value_counts().idxmax()
        if not log_df.empty else "N/A"
    )

    # KPIs principais
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👥 Total de Pessoas no Evento", total_entradas)
    col2.metric("📅 Entradas Hoje", entradas_hoje)
    col3.metric("⏰ Última Entrada", str(ultima_entrada))
    col4.metric("🔥 Pico de Acessos (hora)", str(pico_horario))

    # Gráficos
    st.subheader("📈 Fluxo de Entrada")

    tabs = st.tabs(["📅 Por Dia", "⏰ Por Hora", "⏳ Timeline Completa"])

    with tabs[0]:
        scans_por_dia = log_df.groupby(log_df["DataHora"].dt.date).size().reset_index(name="Entradas")
        chart_dia = alt.Chart(scans_por_dia).mark_bar(color="#4E79A7").encode(
            x="DataHora:T", y="Entradas:Q", tooltip=["DataHora", "Entradas"]
        ).properties(width=700, height=300)
        st.altair_chart(chart_dia, use_container_width=True)

    with tabs[1]:
        scans_por_hora = log_df.groupby(log_df["DataHora"].dt.hour).size().reset_index(name="Entradas")
        chart_hora = alt.Chart(scans_por_hora).mark_bar(color="#F28E2B").encode(
            x="DataHora:O", y="Entradas:Q", tooltip=["DataHora", "Entradas"]
        ).properties(width=700, height=300)
        st.altair_chart(chart_hora, use_container_width=True)

    with tabs[2]:
        timeline = log_df.copy()
        timeline["Contagem"] = range(1, len(timeline) + 1)
        chart_timeline = alt.Chart(timeline).mark_line(point=True, color="#59A14F").encode(
            x="DataHora:T", y="Contagem:Q", tooltip=["DataHora", "Contagem"]
        ).properties(width=700, height=300)
        st.altair_chart(chart_timeline, use_container_width=True)

    # Log completo
    st.subheader("📜 Últimas Leituras Registradas")
    st.dataframe(log_df.tail(20), use_container_width=True)

    # Download
    output = BytesIO()
    log_df.to_excel(output, index=False, engine="openpyxl")
    output.seek(0)
    st.download_button(
        "📥 Baixar Log em Excel",
        data=output,
        file_name="log_entradas.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.markdown("---")
    st.subheader("⚙️ Controles Administrativos")
    colA, colB = st.columns(2)

    with colA:
        if st.button("🔄 Resetar Contagem do Dia (manter histórico)"):
            log_df = log_df[log_df["DataHora"].dt.date != hoje]
            log_df.to_excel(LOG_FILE, index=False)
            st.warning("📉 Contagem de hoje resetada. Histórico preservado.")

    with colB:
        if st.button("🗑️ Resetar Tudo (apaga log)"):
            log_df = pd.DataFrame(columns=["DataHora"])
            log_df.to_excel(LOG_FILE, index=False)
            st.error("🚨 Todo histórico apagado e contagem resetada.")


