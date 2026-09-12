"""
Motor de cálculo da Bússola Tributária.

Porta fiel (e testável) da lógica do simulador em JavaScript. Compara o regime
atual da empresa (Lucro Presumido, Lucro Real, Simples Híbrido ou Simples
Unificado) com os cenários da Reforma Tributária (IVA = IBS + CBS) e
Reforma + Imposto Seletivo, calculando o crédito fornecedor a fornecedor.

Premissas de alíquota são DIDÁTICAS por padrão (IVA 28%, Seletivo 20%) e podem
ser sobrescritas pela entrada. Não substitui a análise de um contador.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

# Alíquotas atuais de PIS/Cofins (didáticas), usadas nos regimes de lucro.
PIS_LP = 0.0365
PIS_LR = 0.0925

Regime = Literal["LP", "LR", "SH", "SU"]
RegimeFornecedor = Literal["Regular", "Hibrido", "Unificado", "Isento"]

REGIME_NOME = {
    "LP": "Lucro Presumido",
    "LR": "Lucro Real",
    "SH": "Simples Híbrido",
    "SU": "Simples Unificado",
}


def is_simples(regime: str) -> bool:
    return regime in ("SH", "SU")


def aprov_of(regime_fornecedor: str, simples_aprov: float) -> float:
    """Fração do IVA da compra que vira crédito, conforme o regime do fornecedor.

    - Regular e Simples Híbrido: crédito pleno (IBS/CBS por fora).
    - Simples Unificado / MEI: repasse pequeno (ajustável, padrão 0).
    - Isento / uso e consumo: nenhum.
    """
    if regime_fornecedor in ("Regular", "Hibrido"):
        return 1.0
    if regime_fornecedor == "Isento":
        return 0.0
    return (simples_aprov or 0.0) / 100.0


@dataclass
class Fornecedor:
    nome: str = ""
    tipo: str = "Mercadoria"  # Mercadoria | Serviço | Locação de bens | Imóveis (locação/arrend.)
    valor: float = 0.0        # R$/mês
    regime: str = "Regular"   # Regular | Hibrido | Unificado | Isento


@dataclass
class Entrada:
    faturamento: float = 100_000.0
    regime: str = "LP"                 # LP | LR | SH | SU
    tem_seletivo: bool = True
    iva: float = 28.0                  # % IVA (IBS + CBS)
    seletivo: float = 20.0             # % Imposto Seletivo
    ipi: float = 15.0                  # % (regime atual)
    icms: float = 18.0                 # % (regime atual)
    is_base: bool = True               # Seletivo entra na base do IVA?
    migrar: bool = False               # simular todos os fornecedores no regime regular
    simples_aprov: float = 0.0         # % de crédito repassado pelo Simples Unificado
    simples_rate: float = 10.0         # % do DAS (alíquota do Simples hoje)
    b2c: bool = False                  # venda para consumidor final (informativo)
    fornecedores: list[Fornecedor] = field(default_factory=list)


def compute_credit(e: Entrada) -> dict:
    """Crédito de IBS/CBS calculado fornecedor a fornecedor."""
    iva = e.iva / 100.0
    compras = credito = potencial = 0.0
    linhas = []
    for sp in e.fornecedores:
        ap = 1.0 if e.migrar else aprov_of(sp.regime, e.simples_aprov)
        c = sp.valor * iva * ap
        compras += sp.valor
        credito += c
        potencial += sp.valor * iva
        linhas.append({
            "nome": sp.nome, "tipo": sp.tipo, "valor": sp.valor,
            "regime": sp.regime, "aproveitamento": ap, "credito": c,
        })
    return {
        "compras": compras,
        "credito": credito,
        "potencial": potencial,
        "vazamento": max(0.0, potencial - credito),
        "linhas": linhas,
    }


def _cenario(liq: float, fat: float) -> dict:
    return {"tributo": round(liq, 2), "carga": (liq / fat) if fat > 0 else 0.0}


def simular(e: Entrada) -> dict:
    """Roda a simulação completa e devolve cenários, crédito e notas."""
    fat = e.faturamento
    ipi, icms, iva, sel = e.ipi / 100, e.icms / 100, e.iva / 100, e.seletivo / 100

    cc = compute_credit(e)
    credito = cc["credito"]

    lp = fat * ipi + fat * icms + fat * PIS_LP
    lr = fat * ipi + fat * icms + fat * PIS_LR
    simp = fat * (e.simples_rate / 100.0)

    # Reforma sem Imposto Seletivo
    ref = max(0.0, fat * iva - credito)
    # Reforma + Imposto Seletivo
    imp_sel = fat * sel
    base_is = fat + imp_sel if e.is_base else fat
    refis = max(0.0, base_is * iva + imp_sel - credito)

    cenarios = {
        "LP": _cenario(lp, fat),
        "LR": _cenario(lr, fat),
        "SIMP": _cenario(simp, fat),
        "REF": _cenario(ref, fat),
        "REFIS": _cenario(refis, fat),
    }

    base_key = "SIMP" if is_simples(e.regime) else e.regime
    ref_key = "REFIS" if e.tem_seletivo else "REF"
    base = cenarios[base_key]
    reforma = cenarios[ref_key]

    dif_mes = reforma["tributo"] - base["tributo"]
    direcao = "sobe" if dif_mes > 1 else ("cai" if dif_mes < -1 else "estável")

    notas = []
    if e.regime == "SU":
        notas.append("simples_unificado")   # não aproveita crédito; migrar libera
    if is_simples(e.regime):
        notas.append("pgdas")               # IVA não compõe base do PGDAS
    if e.b2c:
        notas.append("b2c")                 # consumidor final não aproveita crédito

    return {
        "regime": e.regime,
        "regime_nome": REGIME_NOME.get(e.regime, e.regime),
        "faturamento": fat,
        "cenarios": cenarios,
        "base": {"chave": base_key, **base},
        "reforma": {"chave": ref_key, **reforma},
        "diferenca_mes": round(dif_mes, 2),
        "diferenca_ano": round(dif_mes * 12, 2),
        "direcao": direcao,
        "credito": cc,
        "imposto_seletivo": round(imp_sel, 2),
        "nota_fiscal": {
            "atual": round(fat + fat * ipi, 2),
            "reforma": round(fat + fat * iva, 2),
            "reforma_is": round(fat + base_is * iva, 2),
        },
        "notas": notas,
    }
