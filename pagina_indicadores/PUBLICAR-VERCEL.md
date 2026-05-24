# Como publicar no Vercel

A página é 100% estática (`index.html` + `data.js`), então o deploy é simples e gratuito.
A pasta a publicar é **`pagina_indicadores`**.

## Opção A — Arrastar e soltar (mais fácil, sem instalar nada)

1. Crie uma conta em https://vercel.com (login com Google ou GitHub).
2. No painel, clique em **Add New… → Project**.
3. Procure por **"deploy a static folder"** ou use https://vercel.com/new → aba de upload.
   - Alternativa rápida: acesse https://vercel.com/new e arraste a pasta `pagina_indicadores` inteira.
4. Confirme. Em segundos o Vercel gera um endereço público, ex.: `https://municipio-em-dados.vercel.app`.

> Importante: arraste a pasta **`pagina_indicadores`** (que contém o `index.html`), não a pasta-mãe do projeto.

## Opção B — Pela linha de comando (Vercel CLI)

```bash
npm install -g vercel            # instala a CLI (uma vez)
cd "pagina_indicadores"          # entra na pasta da página
vercel                           # primeiro deploy (faz login no navegador)
vercel --prod                    # publica em produção
```

Na primeira vez ele pergunta o nome do projeto e confirma a pasta. Aceite os padrões.

## Atualizar os dados depois

Sempre que rodar `build_data.py` (gera novo `data.js`):
- **Opção A:** arraste a pasta de novo no painel.
- **Opção B:** rode `vercel --prod` novamente.

## Arquivos da pasta
- `index.html` — a página (cores GestPública, marca d'água com seus contatos).
- `data.js` — dados dos indicadores (gerado pelo `build_data.py`).
- `build_data.py` — script que lê as bases tratadas e regenera o `data.js` (reprodutível).
- Os `.py` não atrapalham o deploy; o Vercel serve só o `index.html`.
