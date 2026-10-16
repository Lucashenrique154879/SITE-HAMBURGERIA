# Campos do cliente.json

Dica: copie o `clientes/chapa-bros/cliente.json` (o comando `--novo` já faz isso) e troque os valores. Textos com `<br/>` quebram linha (só nos campos `nota`).

## marca
| Campo | O que é |
|---|---|
| nome | Nome completo, usado em títulos, pedidos e privacidade |
| linha1 / linha2 | Nome do logo em duas linhas (linha2 aparece na cor de destaque; pode ficar vazio) |
| slogan | Frase curta, aparece no título da home |
| descricao | Descrição para o Google e redes sociais (até ~155 caracteres) |
| rodape | Frase do rodapé |
| logo | Arquivo da logo em `fotos/` (opcional; sem ele usa um ícone de chama) |
| cor_destaque / cor_sobre_destaque | Cor principal (botões, faixa) e a cor do texto sobre ela |
| cor_escura / cor_clara / cor_vermelha | Fundo escuro (cabeçalho, rodapé), fundo claro das seções e cor de rótulos |
| fonte_titulo / fonte_manuscrita | Nome de uma fonte do Google Fonts (ex.: Anton, Bebas Neue, Caveat) |

## contato
whatsapp (só dígitos, 55+DDD+número), telefone, email, instagram/facebook/youtube (links completos; vazio esconde o ícone), horario (texto), horario_estruturado (ex.: `["Tu-Su 11:00-23:00"]`, para o Google), endereco_principal.

## site
dominio (com https://, sem barra no fim), frete_gratis_acima (0 desliga a barra), aviso_topo e aviso_botao (faixa no topo; vazio remove), analytics_id (ex.: G-XXXX), pixel_id, aviso_cookies, moeda.

## paginas_ativas
quiz, como_fazemos, eventos, blog, unidades: `true` ou `false`. Desligar remove a página, o link no menu e as seções da home.

## hero, promo1, promo2, diferenciais, home_historia, chamada_whatsapp, textos
Blocos da home e textos repetidos (faixa "Bateu a fome?", chamada do quiz). Veja o modelo.

## categorias e pratos
- categorias: `id`, `nome`, `foto` (aparece nos círculos da home).
- pratos: `id` (sem espaços ou acentos), `categoria` (id de uma categoria), `nome`, `preco` (número, ex.: 29.9), `foto`, `descricao` (curta), `descricao_longa`, `etiquetas` (ex.: "Mais pedido", "Picante"), `perfil` (lista de [nome, nota de 1 a 5]; pode ser vazia), `contem` (alérgenos; confirme com o cliente), `combina` (ids de outros pratos).
- mais_vendidos: ids dos pratos em destaque na home.
- filtros_perfil: etiquetas usadas como filtro no cardápio (vazio remove o filtro).

## paginas
Cabeçalho (eyebrow, titulo, texto, foto) de cada página.

## historia, como_fazemos, eventos, unidades, blog, faq, depoimentos
Conteúdo de cada página. `depoimentos.itens` deve ter **só depoimentos reais**. Se ficar vazio, a seção some.

## quiz
`perguntas`: cada opção é `[título, subtítulo, {id_do_prato: pontos}]`. `resultados`: para cada prato que pode ser o resultado, o texto e o prato em `combina`. Para desligar, `paginas_ativas.quiz = false`.

## pagamentos
Formas de pagamento oferecidas no carrinho, ex.: `["Pix","Cartão","Dinheiro"]`.
