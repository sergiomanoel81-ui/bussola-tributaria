"""Modelos de entrada/saída da API (Pydantic v2)."""
from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


class FornecedorIn(BaseModel):
    nome: str = ""
    tipo: str = "Mercadoria"
    valor: float = Field(0, ge=0)
    regime: Literal["Regular", "Hibrido", "Unificado", "Isento"] = "Regular"


class SimulacaoIn(BaseModel):
    faturamento: float = Field(100_000, ge=0)
    regime: Literal["LP", "LR", "SH", "SU"] = "LP"
    tem_seletivo: bool = True
    iva: float = Field(28, ge=0, le=100)
    seletivo: float = Field(20, ge=0, le=100)
    ipi: float = Field(15, ge=0, le=100)
    icms: float = Field(18, ge=0, le=100)
    is_base: bool = True
    migrar: bool = False
    simples_aprov: float = Field(0, ge=0, le=100)
    simples_rate: float = Field(10, ge=0, le=100)
    b2c: bool = False
    fornecedores: list[FornecedorIn] = Field(default_factory=list)


class CnpjOut(BaseModel):
    cnpj: str
    razao_social: str | None = None
    nome_fantasia: str | None = None
    regime: Literal["Regular", "Hibrido", "Unificado", "Isento"]
    optante_simples: bool | None = None
    optante_mei: bool | None = None
    situacao: str | None = None
    observacao: str | None = None
