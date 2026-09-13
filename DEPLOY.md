# Bússola Tributária — como rodar e hospedar (Docker)

A aplicação inteira (o **site** + a **API**) roda num **único container**. Isso resolve os dois cenários:

- **Cliente roda na máquina dele** — sem instalar Python nem configurar nada.
- **Cliente quer hospedar** — a *mesma* imagem sobe em qualquer serviço de container.

---

## 1) Rodar localmente (na máquina do cliente)

Pré-requisito: **Docker Desktop** instalado (Windows/Mac) — https://www.docker.com/products/docker-desktop/

Na pasta do projeto:

```bash
docker compose up -d
```

Abra no navegador: **http://localhost:8000**

- `/` → simulador completo
- `/demo/` → versão demonstração
- `/proposta.html` e `/slides.html` → material comercial
- `/docs` → documentação da API

Para parar:

```bash
docker compose down
```

> Sem o compose, dá no mesmo:
> ```bash
> docker build -t bussola-tributaria .
> docker run -p 8000:8000 bussola-tributaria
> ```

---

## 2) Hospedar (se o cliente quiser deixar online)

A imagem é padrão e sobe em qualquer plataforma de container. Ela respeita a
variável de ambiente **`PORT`** (usada por serviços como Render e Railway) e, na
falta dela, usa a `8000`.

**Opção A — Render / Railway (mais simples)**
1. Suba este repositório no GitHub do cliente (ou use o atual).
2. No serviço, crie um **Web Service** a partir do repositório, tipo **Docker**.
3. Pronto — a plataforma detecta o `Dockerfile`, injeta a `PORT` e publica.

**Opção B — VPS com Docker** (DigitalOcean, contabo, etc.)
```bash
docker compose up -d
```
E aponte o domínio/proxy (nginx/Caddy) para a porta 8000.

**Opção C — Qualquer registro de imagem**
```bash
docker build -t seuusuario/bussola-tributaria .
docker push seuusuario/bussola-tributaria
```
E rode a imagem no destino que preferir.

---

## Observações
- A consulta de **CNPJ** funciona direto do navegador (BrasilAPI, gratuita) — não
  exige chave. Para volume alto em produção, trocar por SERPRO/CNPJá com chave.
- Alíquotas (IVA, Seletivo) são **premissas de trabalho** e serão ajustadas conforme
  a regulamentação.
- Nada de dados sensíveis é gravado: hoje o cálculo é feito na hora, sem banco.
  (Persistência/login entram numa etapa futura.)
