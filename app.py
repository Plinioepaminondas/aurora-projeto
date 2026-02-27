import streamlit as st
import spacy
import re
from transformers import pipeline

# -------------------------
# Carregamento dos modelos
# -------------------------
@st.cache_resource
def load_models():
    nlp = spacy.load("pt_core_news_sm")
    # Modelo mais leve para não travar no Streamlit Cloud
    summarizer = pipeline(
        "summarization",
        model="sshleifer/distilbart-cnn-12-6"
    )
    return nlp, summarizer

nlp, summarizer = load_models()

# -------------------------
# Função para extrair entidades
# -------------------------
def extract_entities(text):
    doc = nlp(text)

    medicamentos = []
    sintomas = []
    dosage_pattern = r'\b\d+\s?mg\b'

    # Captura entidades gerais
    for ent in doc.ents:
        if ent.label_ in ["ORG", "MISC"]:
            medicamentos.append(ent.text)

    # Palavras-chave simples para sintomas
    symptom_keywords = [
        "dor", "tontura", "fadiga",
        "febre", "pressão", "infecção",
        "náusea", "vômito"
    ]

    for token in doc:
        if token.text.lower() in symptom_keywords:
            sintomas.append(token.text)

    dosagens = re.findall(dosage_pattern, text)

    return {
        "medicamentos": list(set(medicamentos)),
        "sintomas": list(set(sintomas)),
        "dosagens": list(set(dosagens))
    }

# -------------------------
# Interface Streamlit
# -------------------------
st.set_page_config(page_title="Aurora", layout="centered")

st.title("🩺 Aurora")
st.subheader("Sistema Inteligente de Análise de Prontuários")

st.write("Insira o histórico anterior (opcional) e o prontuário atual para análise.")

previous_text = st.text_area("📜 Histórico Anterior", height=150)
current_text = st.text_area("📝 Prontuário Atual", height=200)

if st.button("🚀 Analisar Prontuário"):

    if not current_text.strip():
        st.warning("Por favor, insira o prontuário atual.")
    else:
        with st.spinner("Processando informações clínicas..."):

            # Extração
            previous_entities = extract_entities(previous_text) if previous_text else {}
            current_entities = extract_entities(current_text)

            # Sumarização
            resumo = summarizer(
                current_text,
                max_length=130,
                min_length=30,
                do_sample=False
            )[0]["summary_text"]

            # Comparação simples
            tags = []
            if previous_text:
                prev_meds = set(previous_entities.get("medicamentos", []))
                curr_meds = set(current_entities.get("medicamentos", []))

                if curr_meds - prev_meds:
                    tags.append("💊 Nova medicação")

                prev_symptoms = set(previous_entities.get("sintomas", []))
                curr_symptoms = set(current_entities.get("sintomas", []))

                if curr_symptoms - prev_symptoms:
                    tags.append("🔴 Novo sintoma detectado")

            # Exibição
            st.subheader("📌 Resumo do Dia")
            st.success(resumo)

            st.subheader("🔎 Entidades Detectadas")
            st.json(current_entities)

            st.subheader("⚠️ Tags de Atenção")

            if tags:
                for tag in tags:
                    st.write(tag)
            else:
                st.write("Nenhuma alteração relevante detectada.")
