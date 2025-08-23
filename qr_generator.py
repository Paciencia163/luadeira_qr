import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from PIL import Image
import os

FILE = "qr_data.xlsx"

# Cria arquivo inicial, se não existir
if not os.path.exists(FILE):
    df = pd.DataFrame([{"ID": 1, "URL": "", "Scans": 0}])
    df.to_excel(FILE, index=False)

st.set_page_config(page_title="Gerador de QR - Luadeira Digital", page_icon="🎟️", layout="wide")

st.title("🎟️ Gerador de QR Code - Luadeira Digital")

# URL base do deploy no Streamlit Cloud
APP_URL = "https://luadeiraqr-eventos.streamlit.app"

# Carregar dados
df = pd.read_excel(FILE)

# Campo para configurar URL de destino
url_destino = st.text_input("🔗 Insira a URL de destino do QR Code:", value=df.loc[0, "URL"])

if st.button("Gerar QR Code"):
    # Atualiza URL no Excel
    df.loc[0, "URL"] = url_destino
    df.to_excel(FILE, index=False)

    # Monta URL completa com base pública
    qr_url = f"{APP_URL}/?qr_id=1"

    # Gerar QR
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Mostrar QR na tela
    st.image(img, caption="QR Code Gerado", use_container_width=False)

    # Permitir download do QR
    buf = BytesIO()
    img.save(buf, format="PNG")
    st.download_button(
        label="⬇️ Baixar QR Code",
        data=buf.getvalue(),
        file_name="qr_code.png",
        mime="image/png"
    )

    st.success("✅ QR Code gerado com sucesso!")
    st.write(f"📲 Quando escaneado, leva para: **{qr_url}**")
