import streamlit as st
import qrcode
from io import BytesIO
from PIL import Image
import pandas as pd
import os

FILE = "qr_data.xlsx"
LOG_FILE = "scans_log.xlsx"

# Inicializa arquivos de dados
if not os.path.exists(FILE):
    df = pd.DataFrame([{"ID": 1, "URL": "", "Scans": 0}])
    df.to_excel(FILE, index=False)

if not os.path.exists(LOG_FILE):
    log_df = pd.DataFrame(columns=["ID", "DataHora"])
    log_df.to_excel(LOG_FILE, index=False)

df = pd.read_excel(FILE)

# Corrige possíveis NaN na contagem
if "Scans" not in df.columns or df.empty:
    df = pd.DataFrame([{"ID": 1, "URL": "", "Scans": 0}])
    df.to_excel(FILE, index=False)

df["Scans"] = df["Scans"].fillna(0).astype(int)

st.set_page_config(page_title="Gerador de QR", page_icon="🛠️")
st.title("🛠️ Gerador de QR Code")

app2_base_url = st.text_input("URL do Leitor (App 2):", "http://localhost:8502")
url = st.text_input("Digite a URL final para redirecionar:")

if st.button("Gerar/Atualizar QR Code") and url:
    df.loc[0, "URL"] = url
    df.to_excel(FILE, index=False)

    redirect_url = f"{app2_base_url}/?qr_id=1"

    qr_img = qrcode.make(redirect_url)
    buf = BytesIO()
    qr_img.save(buf, format="PNG")

    st.image(Image.open(buf), caption="QR Code Único (ID 1)")
    st.download_button("⬇️ Baixar QR Code", data=buf.getvalue(),
                       file_name="qr_code_1.png", mime="image/png")

    st.success("✅ QR Code atualizado!")
    st.write(f"👉 Redireciona para: {url}")
    st.write(f"🔗 Link de leitura: {redirect_url}")
