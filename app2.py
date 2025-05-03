# app2.py
import streamlit as st
from datetime import datetime
from openai import OpenAI
from fpdf import FPDF
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Informações do hotel
info_hotel = {
    "nome": "Compacto Hotel Alphaville Campinas",
    "telefone": "(19) 3262-1525",
    "email": "reservas@compactohotel.com.br",
    "endereco": "Rua Cumarú, 116 – Alphaville Industrial, Campinas – SP, CEP 13098-324",
    "site": "https://compactohotel.com.br",
    "acomodacoes": "Oferecemos suítes compactas com ar-condicionado, Wi-Fi, mesa de trabalho, frigobar e banheiro privativo. Ideal para estadias rápidas e práticas.",
    "sugestoes_proximas": {
        "restaurantes de massa": "Bellini Restaurante, Cantina Brunelli, Cantina Fellini.",
        "restaurantes de frutos do mar": "Coco Bambu (Shopping Iguatemi), Jangada (Shopping D. Pedro),",
        "temos ainda o Outback no Shopping Galleria e Shopping D. Pedro como excelente opção de alimentação": "",
        "pontos_turisticos": "Parque Portugal (Lagoa do Taquaral), Bosque dos Jequitibás, Torre do Castelo.",
        "farmacias": "Drogasil e Droga Raia a menos de 5 minutos do hotel.",
        "padarias": "Padaria Pirâmide, Padaria São Geraldo e Padaria Alemã.",
        "hospitais": "Hospital Vera Cruz e Hospital Samaritano estão a cerca de 10 minutos de carro.",
        "shoppings": "Shopping Galleria, Iguatemi Campinas e Parque Dom Pedro.",
        "aeroporto": "O Aeroporto de Viracopos fica a aproximadamente 25 minutos do hotel.",
                "locadora_carros": "Localiza, Movida e Unidas possuem unidades no Shopping Dom Pedro, Supermercado Carrefour, próximas ao aeroporto e ao centro."
            }
        }

# Instrução de sistema dinâmica com base nas informações do dicionário
system_instruction = (
    f"Você é um assistente virtual do {info_hotel['nome']}. Solicite o nome do hóspede de forma educada no início do atendimento. "
    "Se o usuário não quiser informar o nome, prossiga normalmente com as respostas. Se o nome for fornecido, use-o de forma cordial nas próximas interações. "
    "Você responde exclusivamente sobre hospedagem, turismo e informações úteis da cidade de Campinas. Não mencione outros hotéis. "
    f"Telefone: {info_hotel['telefone']}. Site: {info_hotel['site']}. E-mail: {info_hotel['email']}. Endereço: {info_hotel['endereco']}. "
    f"Acomodações: {info_hotel['acomodacoes']}. "
    f"Sugestões próximas ao hotel:"
    f"- Restaurantes: {info_hotel['sugestoes_proximas']['restaurantes']}"
    f"- Pontos turísticos: {info_hotel['sugestoes_proximas']['pontos_turisticos']}"
    f"- Farmácias: {info_hotel['sugestoes_proximas']['farmacias']}"
    f"- Padarias: {info_hotel['sugestoes_proximas']['padarias']}"
    f"- Hospitais: {info_hotel['sugestoes_proximas']['hospitais']}"
    f"- Shoppings: {info_hotel['sugestoes_proximas']['shoppings']}"
    f"- Aeroporto: {info_hotel['sugestoes_proximas']['aeroporto']}"
    f"- Locadoras de carro: {info_hotel['sugestoes_proximas']['locadora_carros']}."
    "A função de consulta de eventos em tempo real foi desativada."
)

st.set_page_config(page_title="Assistente Virtual - Hotel", page_icon="🏨")
st.title("🧡 Assistente Virtual do Hotel Compacto")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_instruction}]
    st.session_state.user_name = None

# Exibe histórico
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# Entrada do usuário
prompt = st.chat_input("Como posso ajudar com sua estadia ou informações do hotel?")
if prompt:
    # Armazena nome se detectado
    if not st.session_state.user_name and any(p in prompt.lower() for p in ["me chamo", "sou o", "sou a", "meu nome"]):
        partes = prompt.split()
        nome = next((p for i, p in enumerate(partes) if partes[i-1].lower() in ["chamo", "sou", "nome"]), None)
        st.session_state.user_name = nome.capitalize() if nome else None

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("..."):
            client = OpenAI(api_key=OPENAI_API_KEY)
            nome = st.session_state.user_name
            saudacao = f"Olá, {nome}! " if nome else ""
            entrada = f"{saudacao}{prompt}"
            response = client.chat.completions.create(
                model="gpt-4",
                messages=st.session_state.messages + [{"role": "user", "content": entrada}],
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
