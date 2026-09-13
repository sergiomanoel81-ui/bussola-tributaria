"""
API da Bússola Tributária (FastAPI).

Expõe o motor de cálculo e a consulta de CNPJ como serviço. É a base do produto
robusto: cálculo no servidor (versionado), auto-preenchimento de regime por CNPJ
e, adiante, importação de NF-e, persistência e autenticação.

Rodar:  uvicorn app.main:app --reload   (a partir de backend/)
Docs:   http://127.0.0.1:8000/docs
"""
from __future__ import annotations

from dataclasses import asdict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from .engine import Entrada, Fornecedor, simular
from .schemas import SimulacaoIn, CnpjOut
from . import cnpj as cnpj_mod

app = FastAPI(
    title="Bússola Tributária — API",
    version="0.1.0",
    description="Simulador do impacto da Reforma Tributária para PMEs.",
)

# Em produção, restringir aos domínios do front (GitHub Pages / app hospedado).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "servico": "bussola-tributaria", "versao": app.version}


@app.post("/api/simular")
def simular_endpoint(payload: SimulacaoIn) -> dict:
    entrada = Entrada(
        faturamento=payload.faturamento,
        regime=payload.regime,
        tem_seletivo=payload.tem_seletivo,
        iva=payload.iva,
        seletivo=payload.seletivo,
        ipi=payload.ipi,
        icms=payload.icms,
        is_base=payload.is_base,
        migrar=payload.migrar,
        simples_aprov=payload.simples_aprov,
        simples_rate=payload.simples_rate,
        b2c=payload.b2c,
        fornecedores=[Fornecedor(**f.model_dump()) for f in payload.fornecedores],
    )
    return simular(entrada)


@app.get("/api/cnpj/{cnpj}", response_model=CnpjOut)
async def cnpj_endpoint(cnpj: str) -> dict:
    try:
        return await cnpj_mod.consultar_cnpj(cnpj)
    except ValueError as ex:
        raise HTTPException(status_code=400, detail=str(ex))
    except LookupError as ex:
        raise HTTPException(status_code=404, detail=str(ex))
    except Exception:  # noqa: BLE001 — rede/serviço externo indisponível
        raise HTTPException(status_code=502, detail="Consulta de CNPJ indisponível no momento.")


_MODELO = [
    ["Fornecedor", "Fornece", "Valor mensal", "Regime"],
    ["Distribuidora de matéria-prima", "Mercadoria", "18000", "Regular"],
    ["Frete e logística", "Serviço", "6000", "Regular"],
    ["Aluguel do imóvel comercial", "Imóveis (locação/arrend.)", "6000", "Hibrido"],
    ["Embalagens", "Mercadoria", "9000", "Unificado"],
    ["Materiais de uso e consumo", "Mercadoria", "3000", "Isento"],
]


@app.get("/api/modelo.csv")
def modelo_csv() -> PlainTextResponse:
    corpo = "﻿" + "\r\n".join(";".join(linha) for linha in _MODELO)
    return PlainTextResponse(
        corpo,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="modelo-fornecedores.csv"'},
    )


# --- Front-end estático (site + app) servido pela própria API ---
# Mantido POR ÚLTIMO: as rotas /api/* têm prioridade; o resto cai no site.
# Procura a pasta frontend/ tanto rodando local (projeto-bi/frontend) quanto no
# container Docker (/app/frontend).
from pathlib import Path
from fastapi.staticfiles import StaticFiles

_here = Path(__file__).resolve()
for _cand in (_here.parents[2] / "frontend", _here.parents[1] / "frontend", Path.cwd() / "frontend"):
    if _cand.is_dir():
        app.mount("/", StaticFiles(directory=str(_cand), html=True), name="site")
        break
