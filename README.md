# Chapa Bros — site de hamburgueria + kit para vender sites de restaurante

```
.
├── site/        Site publicado (HTML/CSS/JS estático). É isto que a Vercel serve.
├── kit/         Gerador de sites por cliente (gerar.py + modelo + guias). NÃO é publicado.
├── vercel.json  Diz à Vercel para servir a pasta site/ e define cabeçalhos de segurança/cache.
└── .gitignore
```

## Publicar na Vercel
1. Suba esta pasta para um repositório no GitHub.
2. Na Vercel: **Add New → Project → Import** o repositório.
3. Framework Preset: **Other**. Deixe Build Command e Install Command vazios. Não precisa mudar o Output Directory (já está no `vercel.json`).
4. **Deploy**.

Cada `git push` na branch principal publica de novo automaticamente.

## Ver no computador
```
cd site
py -m http.server 8000        (Windows)
python3 -m http.server 8000   (Mac/Linux)
```
Abra http://localhost:8000 (não abra o index.html com duplo clique).

## Gerar o site de um cliente novo
```
cd kit
py gerar.py nome-do-cliente --novo     # cria clientes/nome-do-cliente/cliente.json
# preencha o cliente.json e coloque as fotos em clientes/nome-do-cliente/fotos/
py gerar.py nome-do-cliente            # gera em kit/saida/nome-do-cliente/
```
Para publicar o cliente: copie o conteúdo de `kit/saida/nome-do-cliente/` para a pasta `site/` (ou crie um repositório novo só para ele, com esse conteúdo na raiz — nesse caso o `vercel.json` gerado já está junto). Detalhes em `kit/GUIA-PUBLICACAO.md`.

## Atenção
- Cardápio, preços, unidades, blog e o WhatsApp `5511999990000` da Chapa Bros são **exemplos**. Troque pelos dados reais antes de divulgar.
- O texto de política de privacidade/termos é um modelo, não aconselhamento jurídico.
- O plano Hobby da Vercel é para uso não comercial; para site de cliente pago, use plano Pro ou Netlify/Cloudflare Pages.
