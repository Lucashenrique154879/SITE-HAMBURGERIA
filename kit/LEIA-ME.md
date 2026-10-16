# Kit de site para restaurantes

Gera um site completo (início, cardápio, página de cada prato, quiz, como fazemos, eventos, blog, unidades, contato, privacidade) a partir de **um arquivo por cliente**. O pedido é feito pelo carrinho e enviado ao **WhatsApp** do restaurante. Não precisa de servidor nem banco de dados.

## O que você precisa
- Python 3.8 ou mais novo. Opcional: `pip install pillow` (reduz o tamanho das fotos automaticamente).

## Fluxo para cada cliente novo
1. Criar a pasta do cliente:
   `python3 gerar.py nome-do-cliente --novo`
   Isso cria `clientes/nome-do-cliente/` com `cliente.json` (cópia do modelo) e a pasta `fotos/`.
2. Colocar as fotos do cliente em `clientes/nome-do-cliente/fotos/`.
3. Editar `clientes/nome-do-cliente/cliente.json` com os dados do cliente (veja `REFERENCIA-CAMPOS.md`).
4. Gerar o site:
   `python3 gerar.py nome-do-cliente`
   O site fica em `saida/nome-do-cliente/` e o terminal mostra a **lista de pendências**.
5. Resolver as pendências e gerar de novo, até a lista ficar limpa (ou só com avisos que você aceita).
6. Ver no computador: `python3 -m http.server 8000 -d saida/nome-do-cliente` e abrir http://localhost:8000
7. Publicar: veja `GUIA-PUBLICACAO.md`.

Campos que você não preencher usam o texto do modelo (Chapa Bros), e o relatório avisa quais são. **Nunca entregue com esse aviso na lista.**

## O que o relatório de pendências verifica
- Textos ainda iguais ao modelo, por seção.
- Fotos citadas que não existem na pasta `fotos/`.
- WhatsApp inválido ou ainda fictício.
- Domínio vazio (desliga sitemap, link canônico e imagem de compartilhamento).
- Prato sem preço, categoria ou ids inexistentes (combina com, mais vendidos, quiz).
- Prato sem alérgenos.
- Medição configurada (liga o aviso de cookies sozinho).
- Depoimentos: lembra de usar só os reais e autorizados.

## O que o site faz
- **Carrinho** guardado no navegador, com barra de frete grátis (se configurada), retirada ou entrega, forma de pagamento e observações. O botão final abre o WhatsApp com o pedido pronto.
- **Formulários** (eventos e contato) montam a mensagem e abrem o WhatsApp. Nada é enviado sozinho.
- **SEO:** título, descrição e imagem de compartilhamento por página, dados estruturados de restaurante (Google), `sitemap.xml` e `robots.txt` (com domínio), página 404.
- **LGPD:** página de privacidade com os dados do cliente e aviso de cookies que só carrega Google Analytics e Meta Pixel depois que o visitante aceita.
- **Páginas ligáveis e desligáveis** em `paginas_ativas` (quiz, como fazemos, eventos, blog, unidades).

## O que o site NÃO faz
- Não recebe pagamento online nem guarda pedidos. Tudo passa pelo WhatsApp.
- Não tem painel para o dono editar sozinho. Mudança de cardápio ou preço = editar o `cliente.json` e gerar de novo (ou fazer isso para o cliente como serviço de manutenção).
- Os alérgenos e o "perfil do prato" são informados por você; o site só exibe.

## Pastas
- `modelo/` : arquivos-base (visual, scripts). Mexa aqui só para mudar o visual de todos os clientes.
- `clientes/` : um cliente por pasta. `chapa-bros` é o exemplo completo.
- `saida/` : sites gerados (pode apagar e gerar de novo).
