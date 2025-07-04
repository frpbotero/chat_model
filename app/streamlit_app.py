import streamlit as st
from agent import agent as chat_agent
from ingest_pipeline import ingest_file 
from pathlib import Path
import os


st.set_page_config(page_title="Chat IA", page_icon="🤖", layout="wide")

st.title("🤖 Chat IA com RAG e Ferramentas")

# ───────────────────────────────────────── sidebar – Ingestão ─────────────────────────────────────────
st.sidebar.header("📁 Enviar Documentos para Ingestão")
uploaded_ingest = st.sidebar.file_uploader("Escolha um arquivo", type=["pdf", "txt", "md"], key="ingest")

to_ingest_dir = Path("to_ingest")
to_ingest_dir.mkdir(parents=True, exist_ok=True)

if uploaded_ingest:
    save_path = to_ingest_dir / uploaded_ingest.name
    with open(save_path, "wb") as f:
        f.write(uploaded_ingest.getbuffer())
    st.sidebar.success(f"Arquivo salvo para ingestão: {uploaded_ingest.name}")

# Lista arquivos pendentes
pending_files = list(to_ingest_dir.glob("*"))
if pending_files:
    st.sidebar.markdown("### Arquivos pendentes:")
    for f in pending_files:
        st.sidebar.write("•", f.name)

    if st.sidebar.button("🚀 Processar ingestão"):
        success, failed = 0, 0
        with st.spinner("Processando arquivos…"):
            for f in pending_files:
                try:
                    ingest_file(str(f), version="v1")
                    success += 1
                    f.unlink()
                except Exception as e:
                    st.sidebar.error(f"Erro em {f.name}: {e}")
                    failed += 1
        st.sidebar.success(f"Ingestão concluída: {success} sucesso(s), {failed} erro(s)")
else:
    st.sidebar.info("Nenhum arquivo pendente de ingestão.")

# ───────────────────────────────────────── Main Chat ─────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []

col1, col2 = st.columns((3, 1))

with col1.form("form_pergunta"):
    user_input = st.text_input("Digite sua pergunta:")
    uploaded_context = st.file_uploader("Enviar arquivo de contexto (opcional)", type=["png", "jpg", "jpeg", "txt", "log", "pdf"], key="context")
    submitted = st.form_submit_button("Enviar")

    if submitted and user_input:
        context_note = ""
        if uploaded_context:
            ctx_path = Path("temp_ctx") / uploaded_context.name
            Path("temp_ctx").mkdir(exist_ok=True)
            with open(ctx_path, "wb") as f:
                f.write(uploaded_context.getbuffer())
            context_note = f"\n\n[O usuário enviou o arquivo '{uploaded_context.name}' localizado em '{ctx_path}']"
        with st.spinner("Pensando…"):
            resposta = chat_agent.invoke(user_input + context_note)
            st.session_state.history.append((user_input, resposta, uploaded_context.name if uploaded_context else None))

# ───────────────────────────────────────── Histórico ─────────────────────────────────────────
st.markdown("## 📜 Histórico de Conversa")
for idx, (q, a, attach) in enumerate(reversed(st.session_state.history), 1):
    st.markdown(f"**👤 Pergunta {idx}:** {q}")
    if attach:
        st.markdown(f"📎 Arquivo anexado: {attach}")
    st.markdown(f"**🤖 Resposta:** {a}")
    st.markdown("---")
