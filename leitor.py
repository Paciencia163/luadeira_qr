import streamlit as st
import pandas as pd
import os
from datetime import datetime
import altair as alt

FILE = "qr_data.xlsx"
LOG_FILE = "scans_log.xlsx"

# Inicializa arquivos, se não existirem
if not os.path.exists(FILE):
    df = pd.DataFrame([{"ID": 1, "URL": "", "Scans": 0}])
    df.to_excel(FILE, index=False)

if not os.path.exists(LOG_FILE):
    log_df = pd.DataFrame(columns=["QR_ID", "DataHora"])
    log_df.to_excel(LOG_FILE, index=False)

st.set_page_config(page_title="Leitor de QR - Luadeira Digital", page_icon="📊", layout="wide")

# --- LOGIN ---
if "logado" not in st.session_state:
    st.session_state["logado"] = False

if not st.session_state["logado"]:
    st.title("🔑 Área Administrativa")
    st.markdown("💡 Bem-vindo à **Luadeira Digital**! Faça login para acessar as estatísticas.")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if usuario == "admin" and senha == "1234":  # credenciais simples
            st.session_state["logado"] = True
            st.success("✅ Login realizado com sucesso!")
            st.rerun()
        else:
            st.error("❌ Usuário ou senha incorretos.")

# --- SE LOGADO MOSTRA ESTATÍSTICAS ---
if st.session_state["logado"]:
    # Lê parâmetros da URL
    query_params = st.query_params
    qr_id = int(query_params.get("qr_id", [1])[0])  # padrão = 1

    # Carregar dados
    df = pd.read_excel(FILE)
    log_df = pd.read_excel(LOG_FILE)

    # Se não existe esse QR ainda no Excel, cria
    if qr_id not in df["ID"].values:
        df = pd.concat([df, pd.DataFrame([{"ID": qr_id, "URL": "", "Scans": 0}])], ignore_index=True)
        df.to_excel(FILE, index=False)

    # Normaliza coluna Scans
    df["Scans"] = df["Scans"].fillna(0).astype(int)

    # Incrementa leitura do QR específico
    df.loc[df["ID"] == qr_id, "Scans"] += 1
    df.to_excel(FILE, index=False)

    # Adiciona log
    novo_log = pd.DataFrame([{"QR_ID": qr_id, "DataHora": datetime.now()}])
    log_df = pd.concat([log_df, novo_log], ignore_index=True)
    log_df.to_excel(LOG_FILE, index=False)

    # Interface
    st.title("📊 Estatísticas - Luadeira Digital")
    st.success(f"✅ QR Code **{qr_id}** lido com sucesso!")

    # Mostrar tabela de contagem
    st.subheader("📈 Total de Leituras por QR")
    st.dataframe(df)

    # Estatísticas com gráficos
    st.subheader("📊 Estatísticas de Leitura")

    if not log_df.empty:
        log_df["DataHora"] = pd.to_datetime(log_df["DataHora"], errors="coerce")

        tabs = st.tabs(["📅 Por Dia", "⏰ Por Hora", "🗓️ Por Mês"])

        # --- Scans por Dia ---
        with tabs[0]:
            scans_por_dia = log_df.groupby(log_df["DataHora"].dt.date).size().reset_index(name="Scans")
            chart_dia = alt.Chart(scans_por_dia).mark_bar(color="#4E79A7").encode(
                x=alt.X("DataHora:T", title="Dia"),
                y=alt.Y("Scans:Q", title="Total de Scans"),
                tooltip=["DataHora", "Scans"]
            ).properties(width=700, height=300)
            st.altair_chart(chart_dia, use_container_width=True)

        # --- Scans por Hora ---
        with tabs[1]:
            scans_por_hora = log_df.groupby(log_df["DataHora"].dt.hour).size().reset_index(name="Scans")
            chart_hora = alt.Chart(scans_por_hora).mark_bar(color="#F28E2B").encode(
                x=alt.X("DataHora:O", title="Hora do Dia"),
                y=alt.Y("Scans:Q", title="Total de Scans"),
                tooltip=["DataHora", "Scans"]
            ).properties(width=700, height=300)
            st.altair_chart(chart_hora, use_container_width=True)

        # --- Scans por Mês ---
        with tabs[2]:
            scans_por_mes = log_df.groupby(log_df["DataHora"].dt.to_period("M")).size().reset_index(name="Scans")
            scans_por_mes["DataHora"] = scans_por_mes["DataHora"].astype(str)
            chart_mes = alt.Chart(scans_por_mes).mark_bar(color="#59A14F").encode(
                x=alt.X("DataHora:O", title="Mês"),
                y=alt.Y("Scans:Q", title="Total de Scans"),
                tooltip=["DataHora", "Scans"]
            ).properties(width=700, height=300)
            st.altair_chart(chart_mes, use_container_width=True)
    else:
        st.info("Ainda não há leituras registradas para gerar gráficos.")

    # Botão para limpar apenas os logs (não remove QR)
    if st.button("🗑️ Limpar Log de Leituras"):
        log_df = pd.DataFrame(columns=["QR_ID", "DataHora"])
        log_df.to_excel(LOG_FILE, index=False)
        df["Scans"] = 0
        df.to_excel(FILE, index=False)
        st.warning("📉 Todos os logs de leitura foram apagados e os contadores resetados.")
