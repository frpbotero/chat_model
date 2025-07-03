"""Custom splitters usados no pipeline RAG.

Os métodos retornam instâncias de `TextSplitter` configuradas para tamanhos
específicos de chunk conforme convenções do projeto.
"""
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    TokenTextSplitter,
)


class RecursiveSplitter:
    """Coleção de fábricas para *RecursiveCharacterTextSplitter*.

    Os nomes seguem o padrão `<max_tokens>_<overlap>`, em tokens aproximados.
    """

    @staticmethod
    def chunk_recursive_500_100():
        return RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            add_start_index=True,
        )

    @staticmethod
    def chunk_recursive_1000_200():
        return RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            add_start_index=True,
        )

    @staticmethod
    def chunk_recursive_100_15():
        return RecursiveCharacterTextSplitter(
            chunk_size=100,
            chunk_overlap=15,
            add_start_index=True,
        )

    @staticmethod
    def chunk_recursive_250_40():
        return RecursiveCharacterTextSplitter(
            chunk_size=250,
            chunk_overlap=40,
            add_start_index=True,
        )


class TokenSplitter:
    """Coleção de fábricas para *TokenTextSplitter* com tamanhos fixos."""

    @staticmethod
    def chunk_fixed_size_500_100():
        return TokenTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
        )

    @staticmethod
    def chunk_fixed_size_1000_200():
        return TokenTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )

    @staticmethod
    def chunk_fixed_size_256_50():
        return TokenTextSplitter(
            chunk_size=256,
            chunk_overlap=50,
        )

    @staticmethod
    def chunk_fixed_size_100_25():
        return TokenTextSplitter(
            chunk_size=100,
            chunk_overlap=25,
        )

    @staticmethod
    def chunk_fixed_size_200_40():
        return TokenTextSplitter(
            chunk_size=200,
            chunk_overlap=40,
        )
