"""Agente conversacional (Ollama) com RAG seguro + snippets."""
from __future__ import annotations
from typing import List
from langchain_ollama import ChatOllama
from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType
from langchain.chains import RetrievalQA
from qdrant_client.http.exceptions import UnexpectedResponse

from safe_retriever_wrapper import SafeRetriever
from rag import vectorstore 
from memory import memory
from tools import JiraTool

llm = ChatOllama(model="qwen3:8b", temperature=0)
# promptDefault = ''''
#     Voce é um desenvolvedor senior brasileiro, falante de portugues, onde atua atendendo chamados referente a diversas aplicações da empresa.
#     Caso você não tenha dentro da sua base de dados, deve executar uma busca no rag para trazer as informações necessarias para atender a solicitação.
# '''
# promptLeitor = ''''
#     Voce é um leitor brasileiro, apaixonado pela literatura brasileira, onde sempre que pode esta imerso dentro de obras de renome.
# '''


prompt = ''''
    Voce é um desenvolvedor senior brasileiro, falante de portugues. Sua principal tarefa é responder às perguntas do usuário buscando informações na base de conhecimento.
    SEMPRE use a ferramenta 'Buscar_na_base_conhecimento' primeiro para qualquer pergunta que não seja sobre tarefas específicas do Jira.
    Somente use a ferramenta do Jira se o usuário pedir explicitamente para criar, atualizar ou buscar um ticket. Para todas as outras consultas, comece pela base de conhecimento.
'''


safe_retriever = SafeRetriever()
rag_qa = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=safe_retriever,
    chain_type="stuff",
    return_source_documents=True,
)

def _format_snippets(docs: List, max_docs:int=5, max_chars:int=240)->str:
    if not docs:
        return ""
    lines=[]
    for i,d in enumerate(docs[:max_docs],1):
        src=d.metadata.get("source_file","(desconhecido)")
        snip=d.page_content[:max_chars].replace("\n"," ").strip()
        lines.append(f"{i}. **{src}** – _\"{snip}…\"_")
    return "\n\n**Trechos recuperados**:\n"+"\n".join(lines)

def buscar_no_rag(query:str)->str:
    client = vectorstore.client
    col = vectorstore.collection_name
    total = client.count(collection_name=col, exact=True).count
    if total == 0:
        return f"⚠️ A base de conhecimento está vazia (coleção '{col}')."
    try:
        res = rag_qa.invoke({"query": query})
    except UnexpectedResponse:
        return "⚠️ Erro ao consultar o RAG."
    docs = res["source_documents"]
    if not docs:
        return f"ℹ️ Coleção '{col}' possui {total} vetores, mas nenhum documento relevante encontrado."
    txt = res["result"].replace("",""").replace("",""").replace("","")
    return f"**Total vetores**: {total}\n\n" + txt + _format_snippets(docs)

tools = [
    Tool.from_function(
        func=buscar_no_rag,
        name="Buscar_na_base_conhecimento",
        description="Busca informações no RAG.",
    ),
    JiraTool(),
]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,
    memory=memory,
    handle_parsing_errors=True,
    agent_kwargs={
        "system_message": prompt
    }
)

agente = agent
