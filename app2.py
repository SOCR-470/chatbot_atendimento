# app2.py
import streamlit as st
from datetime import datetime
from openai import OpenAI
from fpdf import FPDF
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Dados reais do hotel
info_hotel = {
    "nome": "Compacto Hotel Alphaville Campinas",
    "telefone": "(19) 3262-1525",
    "email": "reservas@compactohotel.com.br",
    "endereco": "Rua Cumarú, 116 – Alphaville Industrial, Campinas – SP, CEP 13098-324",
    "site": "https://compactohotel.com.br"
}

# Instrução inicial do sistema
system_instruction = (
    f"Você é um assistente virtual do {info_hotel['nome']}. "
    "Responda apenas sobre hospedagem, turismo e informações úteis relacionadas à cidade de Campinas. "
    "Nunca mencione ou compare com outros hotéis. Sempre que possível, informe os dados reais do hotel, como telefone, site, e-mail e endereço. "
    f"Telefone: {info_hotel['telefone']}. Site: {info_hotel['site']}. "
    f"E-mail: {info_hotel['email']}. Endereço: {info_hotel['endereco']}. "
    "A função de consulta de eventos em tempo real foi desativada."
)

st.set_page_config(page_title="Assistente Virtual - Hotel", page_icon="🏨")
st.title("🧡 Assistente Virtual do Hotel Compacto")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_instruction}]

# Exibe histórico
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# Entrada do usuário
prompt = st.chat_input("Como posso ajudar com sua estadia ou informações do hotel?")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("..."):
            client = OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=st.session_state.messages,
                temperature=0
            )
            reply = response.choices[0].message.content
            st.markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})

# Botão de exportação para PDF
if st.button("📥 Baixar conversa em PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f"Conversa com o Assistente do {info_hotel['nome']}\n")
    pdf.ln(5)
    for msg in st.session_state.messages:
        if msg["role"] != "system":
            remetente = "Você" if msg["role"] == "user" else "Assistente"
            texto = f"{remetente}: {msg['content']}\n"
            pdf.multi_cell(0, 10, texto)
            pdf.ln(2)

    pdf_path = "conversa_hotel.pdf"
    pdf.output(pdf_path)
    with open(pdf_path, "rb") as f:
        st.download_button("Clique para baixar o PDF", f, file_name="conversa_hotel.pdf")
