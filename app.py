import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from utils.gerador import gerar_questoes
from utils.leitor_pdf import extrair_texto_pdf
from utils.exportador import exportar_prova
import os
import tempfile

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(
    page_title="EduQuest",
    page_icon="📝",
    layout="centered"
)

st.title("📝 EduQuest")
st.subheader("Gerador de avaliacoes para professores")
st.markdown("---")

st.header("1. Conteudo da avaliacao original")

entrada_tipo = st.radio(
    "Como deseja inserir o conteudo?",
    ["Colar texto", "Upload de PDF"],
    horizontal=True
)

texto_entrada = ""

if entrada_tipo == "Colar texto":
    texto_entrada = st.text_area(
        "Cole aqui o texto da sua prova ou lista:",
        height=300,
        placeholder="Cole as questoes aqui..."
    )
else:
    pdf_arquivo = st.file_uploader("Envie o PDF da prova:", type=["pdf"])
    if pdf_arquivo:
        with st.spinner("Lendo o PDF..."):
            try:
                texto_entrada = extrair_texto_pdf(pdf_arquivo)
                st.success("PDF lido com sucesso!")
                with st.expander("Ver texto extraido do PDF"):
                    st.text(texto_entrada)
            except Exception as e:
                st.error(f"Erro ao ler o PDF: {e}")

st.markdown("---")

st.header("2. Configuracoes da nova avaliacao")

col1, col2 = st.columns(2)

with col1:
    qtd_questoes = st.number_input(
        "Quantidade de questoes:",
        min_value=1,
        max_value=30,
        value=10
    )

with col2:
    tipo_questoes = st.selectbox(
        "Tipo de questoes:",
        ["Objetivas", "Discursivas", "Mistas"]
    )

gerar_gabarito = st.checkbox("Gerar gabarito junto", value=True)

st.markdown("---")

st.header("3. Gerar avaliacao")

if st.button("Gerar avaliacao", type="primary"):
    if not texto_entrada and entrada_tipo == "Colar texto":
        st.warning("Por favor, cole o texto da avaliacao antes de gerar.")
    else:
        with st.spinner("Gerando avaliacao... Aguarde."):
            try:
                resultado = gerar_questoes(
                    texto_entrada,
                    qtd_questoes,
                    tipo_questoes,
                    gerar_gabarito
                )
                st.session_state["questoes_geradas"] = resultado
            except Exception as e:
                st.error(f"Erro ao gerar avaliacao: {e}")

if "questoes_geradas" in st.session_state:
    st.markdown("---")
    st.header("4. Avaliacao gerada")
    
    questoes_editadas = st.text_area(
        "Questoes geradas (você pode editar antes de exportar):",
        value=st.session_state["questoes_geradas"],
        height=500,
        key="editor_questoes"
    )
    st.session_state["questoes_geradas"] = questoes_editadas

    st.markdown("---")
    st.header("5. Exportar")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Exportar Prova (Word)", type="primary"):
            with st.spinner("Gerando arquivo Word..."):
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_prova:
                        caminho_prova = tmp_prova.name
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_gabarito:
                        caminho_gabarito = tmp_gabarito.name

                    exportar_prova(
                        st.session_state["questoes_geradas"],
                        caminho_prova,
                        caminho_gabarito
                    )

                    with open(caminho_prova, "rb") as f:
                        st.download_button(
                            label="Baixar Prova.docx",
                            data=f,
                            file_name="Prova.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                except Exception as e:
                    st.error(f"Erro ao exportar prova: {e}")

    with col2:
        if gerar_gabarito:
            if st.button("Exportar Gabarito (Word)"):
                with st.spinner("Gerando arquivo Word..."):
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_prova:
                            caminho_prova = tmp_prova.name
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_gabarito:
                            caminho_gabarito = tmp_gabarito.name

                        exportar_prova(
                            st.session_state["questoes_geradas"],
                            caminho_prova,
                            caminho_gabarito
                        )

                        with open(caminho_gabarito, "rb") as f:
                            st.download_button(
                                label="Baixar Gabarito.docx",
                                data=f,
                                file_name="Gabarito.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )
                    except Exception as e:
                        st.error(f"Erro ao exportar gabarito: {e}")