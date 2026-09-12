"""Testes do motor de cálculo — validam os números conhecidos do simulador."""
import pytest

from app.engine import Entrada, Fornecedor, simular, aprov_of
from app.cnpj import inferir_regime, normaliza_cnpj


def _fornecedores_exemplo():
    return [
        Fornecedor("Distribuidora", "Mercadoria", 18000, "Regular"),
        Fornecedor("Frete", "Serviço", 6000, "Regular"),
        Fornecedor("Aluguel", "Imóveis (locação/arrend.)", 6000, "Hibrido"),
        Fornecedor("Embalagens", "Mercadoria", 9000, "Unificado"),
        Fornecedor("Uso e consumo", "Mercadoria", 3000, "Isento"),
    ]


def test_lucro_presumido_sem_fornecedores():
    r = simular(Entrada(faturamento=100_000, regime="LP", fornecedores=[]))
    assert r["cenarios"]["LP"]["tributo"] == pytest.approx(36_650)
    assert r["cenarios"]["LP"]["carga"] == pytest.approx(0.3665)
    assert r["cenarios"]["LR"]["tributo"] == pytest.approx(42_250)
    # Sem crédito: reforma = IVA cheio
    assert r["cenarios"]["REF"]["tributo"] == pytest.approx(28_000)
    assert r["cenarios"]["REFIS"]["tributo"] == pytest.approx(53_600)


def test_credito_por_fornecedor():
    r = simular(Entrada(faturamento=100_000, regime="LP",
                        fornecedores=_fornecedores_exemplo()))
    # Regular (24k) + Híbrido (6k) = 30k * 28% = 8.400; Unificado/Isento = 0
    assert r["credito"]["credito"] == pytest.approx(8_400)
    assert r["credito"]["compras"] == pytest.approx(42_000)
    assert r["cenarios"]["REF"]["tributo"] == pytest.approx(19_600)
    assert r["cenarios"]["REFIS"]["tributo"] == pytest.approx(45_200)
    assert r["cenarios"]["REFIS"]["carga"] == pytest.approx(0.452)


def test_migrar_usa_credito_potencial():
    r = simular(Entrada(faturamento=100_000, migrar=True,
                        fornecedores=_fornecedores_exemplo()))
    assert r["credito"]["credito"] == pytest.approx(11_760)  # 42.000 * 28%
    assert r["credito"]["vazamento"] == pytest.approx(0)


def test_simples_unificado_usa_das_como_base():
    r = simular(Entrada(faturamento=100_000, regime="SU", simples_rate=10,
                        fornecedores=_fornecedores_exemplo()))
    assert r["base"]["chave"] == "SIMP"
    assert r["base"]["tributo"] == pytest.approx(10_000)
    assert r["base"]["carga"] == pytest.approx(0.10)
    assert "simples_unificado" in r["notas"]
    assert "pgdas" in r["notas"]
    assert r["direcao"] == "sobe"


def test_diferenca_anual():
    r = simular(Entrada(faturamento=100_000, regime="LP",
                        fornecedores=_fornecedores_exemplo()))
    # REFIS 45.200 - LP 36.650 = 8.550/mês
    assert r["diferenca_mes"] == pytest.approx(8_550)
    assert r["diferenca_ano"] == pytest.approx(102_600)


def test_b2c_gera_nota():
    r = simular(Entrada(b2c=True, fornecedores=[]))
    assert "b2c" in r["notas"]


def test_aprov_of():
    assert aprov_of("Regular", 0) == 1.0
    assert aprov_of("Hibrido", 0) == 1.0
    assert aprov_of("Isento", 50) == 0.0
    assert aprov_of("Unificado", 20) == pytest.approx(0.20)


def test_inferir_regime():
    assert inferir_regime({"opcao_pelo_mei": True})[0] == "Unificado"
    assert inferir_regime({"opcao_pelo_simples": True})[0] == "Unificado"
    assert inferir_regime({"opcao_pelo_simples": False})[0] == "Regular"


def test_normaliza_cnpj():
    assert normaliza_cnpj("12.345.678/0001-99") == "12345678000199"
