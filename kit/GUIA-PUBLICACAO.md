# Publicar o site de um cliente

O site é só arquivos (HTML, CSS, JS e fotos). Qualquer hospedagem de arquivos estáticos serve. O conteúdo que você publica é a pasta `saida/nome-do-cliente/`.

## Antes de publicar (checklist)
- [ ] `python3 gerar.py cliente` sem pendências de "Texto de exemplo" nem "Foto".
- [ ] WhatsApp testado: abrir o site, adicionar um item, enviar pelo WhatsApp e ver a mensagem chegar no número certo.
- [ ] Cardápio, preços e alérgenos conferidos pelo cliente, por escrito.
- [ ] Horários e endereços conferidos.
- [ ] Depoimentos: só reais e autorizados (ou seção vazia).
- [ ] Fotos: do próprio restaurante ou com autorização de uso.
- [ ] Testar no celular (a maior parte dos pedidos vem de lá).
- [ ] `dominio` preenchido com o endereço final (https://...).

## Opção 1: Netlify (mais simples)
1. Criar conta em netlify.com (grátis).
2. "Add new site" → "Deploy manually" → arrastar a pasta `saida/nome-do-cliente`.
3. Para domínio próprio: "Domain settings" → "Add a domain" e seguir as instruções de DNS.
4. Para atualizar: arrastar a pasta de novo.

## Opção 2: Cloudflare Pages
1. dash.cloudflare.com → Workers & Pages → Create → Pages → "Upload assets".
2. Enviar a pasta `saida/nome-do-cliente`.
3. Conectar o domínio em "Custom domains".

## Opção 3: Vercel
A pasta de saída já é um site pronto, sem etapa de build. O gerador cria um `vercel.json` com cabeçalhos de segurança e cache.

Pelo terminal (precisa de Node.js):
1. `npm i -g vercel` e `vercel login` (uma vez só).
2. `cd saida/nome-do-cliente`
3. `vercel --prod`. Nas perguntas: escolha o seu escopo, "Link to existing project? No", e deixe o resto no padrão (sem framework, sem build command, diretório atual).
4. Para atualizar, gere de novo e rode `vercel --prod` outra vez na mesma pasta.

Pelo painel (sem terminal): vercel.com → Add New → Project → suba a pasta `saida/nome-do-cliente` por um repositório no GitHub; em "Framework Preset" escolha **Other**, deixe Build Command vazio e Output Directory como `.`.

Domínio: Project → Settings → Domains → Add, e siga os registros DNS que a Vercel mostrar. A página `404.html` é usada automaticamente.

Dica: use uma conta Vercel por cliente (ou um time) se for transferir o projeto depois. O plano grátis (Hobby) da Vercel é para uso pessoal e não comercial. Para site de cliente que paga, use o plano Pro ou prefira Netlify ou Cloudflare Pages.

## Opção 4: hospedagem comum (cPanel/FTP)
Enviar o conteúdo da pasta para `public_html`.

## Domínio
- Domínio .com.br: registro.br (cerca de R$ 40 por ano). Domínio é do cliente: registre no nome e e-mail dele.
- Aponte o DNS conforme a hospedagem pedir (registros A/CNAME). O HTTPS é automático nas opções acima.

## Depois de publicar
1. **Google Search Console** (search.google.com/search-console): adicionar o site e enviar `https://dominio/sitemap.xml`.
2. **Google Meu Negócio**: criar ou atualizar a ficha do restaurante com o link do site e o link do cardápio. Isso traz mais clientes que o próprio site.
3. **Instagram/WhatsApp Business**: colocar o link do site na bio.
4. **Analytics** (opcional): criar a propriedade no Google Analytics, copiar o ID (G-XXXX) para `analytics_id`, gerar e publicar de novo. O aviso de cookies aparece sozinho.
5. Testar de novo no celular com o domínio final.

## Manutenção (serviço mensal opcional)
- Troca de cardápio, preços e fotos: editar `cliente.json`, gerar e publicar.
- Atualizar o blog e as promoções.
- Conferir o WhatsApp e os horários nas datas especiais.
