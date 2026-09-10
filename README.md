# Projeto BI

Kit inicial de Business Intelligence em Python. Estrutura pronta pra analisar
dados, gerar graficos e montar dashboards.

## Estrutura
```
projeto-bi/
  data/         -> seus dados (CSV, Excel). Ja vem com exemplo_vendas.csv
  notebooks/    -> analises exploratorias em Jupyter
  src/          -> codigo (ex.: dashboard.py em Streamlit)
  output/       -> graficos e relatorios exportados
  requirements.txt
```

## Como usar (Windows / PowerShell)

1. Ativar o ambiente virtual (ja criado):
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   (Voce vai ver `(.venv)` no inicio da linha do terminal.)

2. Rodar o dashboard de exemplo:
   ```powershell
   streamlit run src/dashboard.py
   ```
   Abre no navegador em http://localhost:8501

3. Abrir o Jupyter pra analise:
   ```powershell
   jupyter lab
   ```

4. Quando terminar, sair do ambiente:
   ```powershell
   deactivate
   ```

## Trocar pelos seus dados
Coloque seu arquivo em `data/` e ajuste o caminho no comeco do `src/dashboard.py`
(ou no notebook). O codigo de exemplo le `data/exemplo_vendas.csv`.

## Bibliotecas incluidas
pandas, numpy, openpyxl, matplotlib, seaborn, plotly, streamlit, jupyterlab, SQLAlchemy
