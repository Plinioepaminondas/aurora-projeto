import streamlit as st
import re

# -------------------------
# Função para extrair "entidades"
# -------------------------
def extract_entities(text):
    # Medicações simples: palavras com "mg"
    medicamentos = re.findall(r'\b[\w\s]+?\d+\s?mg\b', text, flags=re.IGNORECASE)
    
    # Sintomas simples
    symptom_keywords = ["dor", "tontura", "fadiga", "febre", "pressão", "infecção", "náusea", "vômito"]
    sintomas = [word for word in symptom_keywords if word.lower() in text.lower()]
    
    return {
        "medicamentos": list(set(medicamentos)),
        "sintomas": list(set(sintomas))
    }

# -------------------------
# Função para resumo simples
# -------------------------
def summarize_text(text, max_sentences=3):
    sentences = text.split(".")
    resumo = ". ".join(sentences[:max_sentences])
    if not resumo.endswith("."):
        resumo += "."
    return resumo

# -------------------------
# Interface Streamlit
# -------------------------
st.set_page_config(page_title="Aurora", layout="centered")

st.title("🩺 Aurora - Versão Estável Cloud")
st.subheader("Resumo de Prontuários e Detecção de Alterações")

previous_text = st.text_area("📜 Histórico Anterior", height=150)
current_text = st.text_area("📝 Prontuário Atual", height=200)

if st.button("🚀 Analisar Prontuário"):
    if not current_text.strip():
        st.warning("Por favor, insira o prontuário atual.")
    else:
        # Extração de entidades
        previous_entities = extract_entities(previous_text) if previous_text else {}
        current_entities = extract_entities(current_text)

        # Resumo simples
        resumo = summarize_text(current_text)

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
