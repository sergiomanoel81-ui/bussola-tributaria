"""Gera um dataset de exemplo (vendas) em data/exemplo_vendas.csv.
Usa apenas a biblioteca padrao do Python - nao precisa do venv.
"""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)

produtos = {
    "Notebook":      ("Eletronicos", 3500),
    "Mouse":         ("Acessorios", 80),
    "Teclado":       ("Acessorios", 150),
    "Monitor":       ("Eletronicos", 900),
    "Cadeira":       ("Moveis", 700),
    "Mesa":          ("Moveis", 450),
    "Headset":       ("Acessorios", 250),
    "Webcam":        ("Acessorios", 200),
}
regioes = ["Sudeste", "Sul", "Nordeste", "Centro-Oeste", "Norte"]
vendedores = ["Ana", "Bruno", "Carla", "Diego", "Elaine"]

inicio = date(2025, 1, 1)
linhas = []
for _ in range(500):
    prod = random.choice(list(produtos))
    categoria, preco_base = produtos[prod]
    preco = round(preco_base * random.uniform(0.9, 1.1), 2)
    qtd = random.randint(1, 8)
    dia = inicio + timedelta(days=random.randint(0, 364))
    linhas.append({
        "data": dia.isoformat(),
        "produto": prod,
        "categoria": categoria,
        "regiao": random.choice(regioes),
        "vendedor": random.choice(vendedores),
        "quantidade": qtd,
        "preco_unitario": preco,
        "total": round(preco * qtd, 2),
    })

linhas.sort(key=lambda r: r["data"])

out = Path(__file__).resolve().parent.parent / "data" / "exemplo_vendas.csv"
with open(out, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
    writer.writeheader()
    writer.writerows(linhas)

print(f"OK: {len(linhas)} vendas geradas em {out}")
