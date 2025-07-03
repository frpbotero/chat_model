from langchain.tools import BaseTool

class JiraTool(BaseTool):
    """Ferramenta simulada que consulta tickets em um sistema JIRA interno."""

    name: str = "Consultar_JIRA"
    description: str = "Consulta tickets JIRA usando uma API interna."

    def _run(self, query: str) -> str:  # type: ignore[override]
        # Aqui você poderia integrar um SDK real do JIRA.
        return f"[JIRA Simulado] Resultado para: '{query}'"

    def _arun(self, *args, **kwargs):
        raise NotImplementedError("Execução assíncrona não suportada.")
