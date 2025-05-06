import streamlit as st
from datetime import datetime
from openai import OpenAI
from fpdf import FPDF
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

info_hotel = {
    "nome": "Compacto Hotel Alphaville Campinas",
    "telefone": "(19) 3262-1525",
    "email": "reservas@compactohotel.com.br",
    "endereco": "Rua Cumarú, 116 – Alphaville Industrial, Campinas – SP, CEP 13098-324",
    "site": "https://compactohotel.com.br",
    "acomodacoes": "Oferecemos 54 apartamentos em 3 categorias: Standard, Superior e Máster/executivo nos formatos Individuais, duplos e triplos, todas com ar-condicionado, Wi-Fi, mesa de trabalho, frigobar e banheiro privativo.",
    "cafe_da_manha": "Nosso café da manhã é incluso em todas as tarifas e oferece bolos caseiros, pães diversos, ovos mexidos, frutas de época, cereais, leite, café, chás, chocolate quente, iogurte e sucos variados.",
    "estrutura": "Estacionamento, Espaço Health, Internet e Fitness Center e Business Center.",
    "quartos": "Compacto Single, Compacto Twin, Compacto Casal, Triplo Casal, Triplo Solteiro, Master Casal.",
    "resumo_servicos_estrutura": (
        "Seja muito bem-vindo! O Compacto Hotel Alphaville Campinas é ideal para quem busca conforto com praticidade. Contamos com 54 apartamentos modernos nas categorias Standard, Superior e Máster, todos bem equipados para sua comodidade. Além disso, oferecemos estacionamento gratuito, Wi-Fi, recepção 24h, Espaço Health, Fitness Center e Business Center para garantir uma experiência completa."
    ),
    "forma_pagamento_localizacao": (
        "Aceitamos diversas formas de pagamento: dinheiro, cartões de crédito, débito e PIX. O hotel está estrategicamente localizado na Rua Cumarú, 116 – Alphaville Industrial, com acesso rápido ao centro de Campinas e ao Aeroporto de Viracopos."
    ),
    "restricoes": (
        "Atualmente, não aceitamos animais de estimação, exceto cães-guia. O horário de check-in é a partir das 14h e o check-out deve ser realizado até às 12h."
    ),
    "contatos": (
        "📞 Telefone: (19) 3262-1525\n📧 E-mail: reservas@compactohotel.com.br\n🌐 Site: https://compactohotel.com.br"
    ),
    "sugestoes_proximas": {
        "restaurantes": "Bellini Restaurante, Cantina Brunelli, Cantina Fellini, Coco Bambu (Shopping Iguatemi), Jangada (Shopping D. Pedro), Outback (Galleria e D. Pedro).",
        "pontos_turisticos": "Parque Portugal (Lagoa do Taquaral), Bosque dos Jequitibás, Torre do Castelo.",
        "farmacias": "Drogasil e Droga Raia a menos de 5 minutos do hotel.",
        "padarias": "Padaria Pirâmide, Padaria São Geraldo e Padaria Alemã.",
        "hospitais": "Hospital Vera Cruz e Hospital Samaritano a cerca de 10 minutos.",
        "shoppings": "Galleria, Iguatemi Campinas e Parque Dom Pedro.",
        "aeroporto": "Aeroporto de Viracopos a aproximadamente 25 minutos.",
        "locadora_carros": "Localiza, Movida e Unidas no Shopping Dom Pedro, Carrefour e próximo ao aeroporto."
    }
}

system_instruction = (
    f"Você é um assistente virtual do {info_hotel['nome']}. Solicite o nome do hóspede no início do atendimento. Se não quiser informar, prossiga normalmente. Se informar, use-o cordialmente. "
    "Você responde exclusivamente sobre o hotel, hospedagem, turismo e serviços úteis em Campinas. Não mencione outros estabelecimentos. "
    "Evite desculpas desnecessárias. Use tom positivo e informativo. Organize respostas por etapas:"
    "(1) primeiro um resumo animado e cordial dos serviços e estrutura; (2) depois formas de pagamento e localização; (3) restrições; (4) contatos."
    "Ao identificar mais de 3 repetições idênticas da mesma pergunta, oriente com educação e encerre o atendimento. "
    f"Telefone: {info_hotel['telefone']}. Site: {info_hotel['site']}. E-mail: {info_hotel['email']}. Endereço: {info_hotel['endereco']}"
)

st.set_page_config(page_title="Assistente Virtual - Hotel", page_icon="🏨")
st.title("🧡 Dani, Assistente Virtual do Hotel Compacto")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_instruction}]
    st.session_state.user_name = None
    st.session_state.nivel_info_hotel = 0
    st.session_state.contagem_interacoes = 0
    st.session_state.historico_perguntas = []

for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

prompt = st.chat_input("Como posso ajudar com sua estadia ou informações do hotel?")
if prompt:
    st.session_state.contagem_interacoes += 1
    st.session_state.historico_perguntas.append(prompt)

    repeticoes = st.session_state.historico_perguntas.count(prompt)
    if repeticoes > 3 or st.session_state.contagem_interacoes > 15:
        resposta_final = (
            "Notei que a mesma pergunta foi repetida diversas vezes. Para garantir um atendimento eficiente, vamos encerrar por agora. "
            "Caso deseje mais informações, estamos à disposição pelos canais oficiais:"
            f"\n{info_hotel['contatos']}"
        )
        with st.chat_message("assistant"):
            st.markdown(resposta_final)
        st.stop()

    if not st.session_state.user_name and any(p in prompt.lower() for p in ["me chamo", "sou o", "sou a", "meu nome"]):
        partes = prompt.split()
        nome = next((p for i, p in enumerate(partes) if partes[i-1].lower() in ["chamo", "sou", "nome"]), None)
        st.session_state.user_name = nome.capitalize() if nome else None

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("..."):
            nome = st.session_state.user_name
            saudacao = f"Olá, {nome}! " if nome else ""

            if "hotel" in prompt.lower():
                nivel = st.session_state.get("nivel_info_hotel", 0)
                if nivel == 0:
                    resposta = saudacao + info_hotel["resumo_servicos_estrutura"]
                    st.session_state.nivel_info_hotel = 1
                elif nivel == 1:
                    resposta = info_hotel["forma_pagamento_localizacao"]
                    st.session_state.nivel_info_hotel = 2
                elif nivel == 2:
                    resposta = info_hotel["restricoes"]
                    st.session_state.nivel_info_hotel = 3
                else:
                    resposta = info_hotel["contatos"]
            else:
                client = OpenAI(api_key=OPENAI_API_KEY)
                entrada = f"{saudacao}{prompt}"
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=st.session_state.messages + [{"role": "user", "content": entrada}],
                    temperature=0
                )
                resposta = response.choices[0].message.content

            st.markdown(resposta)
            st.session_state.messages.append({"role": "assistant", "content": resposta})

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
