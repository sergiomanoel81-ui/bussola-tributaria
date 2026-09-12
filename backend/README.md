# Bússola Tributária — Backend (API)

Base do produto **robusto**: o motor de cálculo da Reforma Tributária exposto como
serviço (FastAPI), com consulta de CNPJ para preencher o regime dos fornecedores
automaticamente. O front estático (GitHub Pages) calcula no navegador; esta API
traz o que o navegador não faz sozinho: consulta de CNPJ, cálculo versionado no
servidor e — próximos passos — importação de NF-e, persistência e login.

## Rodar (Windows / PowerShell)

```powershell
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

- API:  http://127.0.0.1:8000
- Docs interativas (Swagger): http://127.0.0.1:8000/docs

## Endpoints

| Método | Rota | O que faz |
|--------|------|-----------|
| GET  | `/api/health` | Verifica se a API está no ar |
| POST | `/api/simular` | Roda a simulação (mesmo motor do front) |
| GET  | `/api/cnpj/{cnpj}` | Consulta CNPJ (BrasilAPI) e infere o regime |
| GET  | `/api/modelo.csv` | Baixa o modelo de planilha de fornecedores |

### Exemplo — POST /api/simular

```json
{
  "faturamento": 100000,
  "regime": "LP",
  "iva": 28,
  "seletivo": 20,
  "fornecedores": [
    {"nome": "Distribuidora", "tipo": "Mercadoria", "valor": 18000, "regime": "Regular"},
    {"nome": "Embalagens", "tipo": "Mercadoria", "valor": 9000, "regime": "Unificado"}
  ]
}
```

## Testes

```powershell
cd backend
pytest
```

## Notas
- Alíquotas (IVA 28%, Seletivo 20%) são **premissas didáticas**, não valores oficiais.
- Consulta de CNPJ usa a **BrasilAPI** (gratuita). Para produção com volume, trocar
  por SERPRO/CNPJá com chave.
- `Simples Híbrido` não é inferível pelo CNPJ (é uma opção da empresa a partir de
  2027); optantes do Simples são classificados como `Unificado` por padrão.
