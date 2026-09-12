"""
Consulta de CNPJ (BrasilAPI) e inferência do regime do fornecedor.

A consulta preenche automaticamente o regime de cada fornecedor no mapa de
créditos — o maior salto de valor do produto robusto. A BrasilAPI é gratuita e
pública; para produção com volume, trocar por SERPRO/CNPJá com chave.
"""
from __future__ import annotations

import re

BRASILAPI_URL = "https://brasilapi.com.br/api/cnpj/v1/{cnpj}"


def normaliza_cnpj(cnpj: str) -> str:
    return re.sub(r"\D", "", cnpj or "")


def inferir_regime(dados: dict) -> tuple[str, str]:
    """Mapeia a resposta da BrasilAPI para o regime usado no simulador.

    Retorna (regime, observacao). Não é possível inferir 'Simples Híbrido' pela
    base: híbrido é uma OPÇÃO da empresa a partir de 2027, não um dado cadastral.
    Por isso um optante do Simples é classificado como 'Unificado' por padrão.
    """
    mei = bool(dados.get("opcao_pelo_mei"))
    simples = bool(dados.get("opcao_pelo_simples"))
    if mei:
        return "Unificado", "MEI — DAS cheia, sem crédito na entrada."
    if simples:
        return ("Unificado",
                "Optante do Simples. Se aderir ao Simples Híbrido (2027), muda para 'Hibrido'.")
    return "Regular", "Não optante do Simples — regime regular (crédito pleno)."


async def consultar_cnpj(cnpj: str) -> dict:
    """Busca o CNPJ na BrasilAPI e devolve os dados + regime inferido.

    Levanta ValueError (CNPJ inválido) ou LookupError (não encontrado / falha).
    """
    import httpx  # import tardio: mantém o motor utilizável sem a dependência

    doc = normaliza_cnpj(cnpj)
    if len(doc) != 14:
        raise ValueError("CNPJ deve ter 14 dígitos.")

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(BRASILAPI_URL.format(cnpj=doc))
    if resp.status_code == 404:
        raise LookupError("CNPJ não encontrado.")
    if resp.status_code != 200:
        raise LookupError(f"Falha na consulta (HTTP {resp.status_code}).")

    dados = resp.json()
    regime, obs = inferir_regime(dados)
    return {
        "cnpj": doc,
        "razao_social": dados.get("razao_social"),
        "nome_fantasia": dados.get("nome_fantasia"),
        "regime": regime,
        "optante_simples": bool(dados.get("opcao_pelo_simples")),
        "optante_mei": bool(dados.get("opcao_pelo_mei")),
        "situacao": dados.get("descricao_situacao_cadastral"),
        "observacao": obs,
    }
