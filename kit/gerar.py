#!/usr/bin/env python3
"""Gerador de site para restaurantes.
Uso:  python3 gerar.py <pasta-do-cliente> [--artefato]
Lê clientes/<cliente>/cliente.json (+ fotos/), gera saida/<cliente>/ e mostra o relatório de pendências."""
import json, os, re, sys, shutil, html, copy
from pathlib import Path
KIT = Path(__file__).resolve().parent
MOD = KIT / 'modelo'
DEMO_NAME = 'chapa-bros'

def merge(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        r = dict(a)
        for k, v in b.items(): r[k] = merge(a[k], v) if k in a else v
        return r
    return b
def e(s): return html.escape(str(s), quote=True)
def slugify(s): return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not args: sys.exit(__doc__)
    nome = args[0].rstrip('/').split('/')[-1]
    if '--novo' in sys.argv:
        dst = KIT / 'clientes' / nome
        if dst.exists(): sys.exit('Já existe: %s' % dst)
        (dst / 'fotos').mkdir(parents=True)
        shutil.copy(KIT / 'clientes' / DEMO_NAME / 'cliente.json', dst / 'cliente.json')
        open(dst / 'fotos' / 'COLOQUE-AS-FOTOS-AQUI.txt', 'w').write('Coloque aqui as fotos do cliente (jpg ou png) e use os nomes dos arquivos no cliente.json.\n')
        print('Criado: %s\nEdite %s/cliente.json e rode: python3 gerar.py %s' % (dst, dst, nome)); return
    artefato = '--artefato' in sys.argv
    cdir = KIT / 'clientes' / nome
    if not (cdir / 'cliente.json').exists(): sys.exit('Não achei %s/cliente.json' % cdir)
    demo = json.load(open(KIT / 'clientes' / DEMO_NAME / 'cliente.json', encoding='utf-8'))
    raw = json.load(open(cdir / 'cliente.json', encoding='utf-8'))
    C = merge(demo, raw) if nome != DEMO_NAME else raw
    out = KIT / 'saida' / (nome + ('-artefato' if artefato else ''))
    shutil.rmtree(out, ignore_errors=True); (out / 'fotos').mkdir(parents=True)
    G = Gerador(C, raw, demo, cdir, out, nome, artefato)
    G.rodar()

class Gerador:
    def __init__(s, C, raw, demo, cdir, out, nome, artefato):
        s.C, s.raw, s.demo, s.cdir, s.out, s.nome, s.artefato = C, raw, demo, cdir, out, nome, artefato
        s.icones = json.load(open(MOD / 'icones.json', encoding='utf-8'))
        s.avisos = []; s.fotos = {}
        s.M = C['marca']; s.K = C['contato']; s.S = C['site']
        s.on = C['paginas_ativas']
        s.moeda = s.S.get('moeda', 'R$')
        s.pratos = C['pratos']; s.byid = {p['id']: p for p in s.pratos}
        s.cats = {c['id']: c for c in C['categorias']}

    # ---------- utilidades ----------
    def brl(s, v): return s.moeda + ' ' + ('%.2f' % v).replace('.', ',')
    def ic(s, nome, cls='h-4 w-4'):
        svg = s.icones[nome]
        return re.sub(r'class="[^"]*"', 'class="lucide %s"' % cls, svg, count=1)
    def foto(s, f):
        """registra a foto usada e devolve o caminho no site"""
        if not f: return ''
        s.fotos[f] = True
        return 'fotos/' + f
    def copiar_fotos(s):
        try:
            from PIL import Image
        except ImportError:
            Image = None
        for f in s.fotos:
            src = s.cdir / 'fotos' / f
            if not src.exists():
                s.avisos.append(('Foto', 'Arquivo não encontrado em fotos/: %s' % f)); continue
            dst = s.out / 'fotos' / f
            if Image and f.lower().endswith(('.jpg', '.jpeg', '.png')):
                im = Image.open(src)
                if im.width > 1600: im = im.resize((1600, round(im.height * 1600 / im.width)))
                if f.lower().endswith('.png'): im.save(dst, optimize=True)
                else: im.convert('RGB').save(dst, quality=82, optimize=True, progressive=True)
            else: shutil.copy(src, dst)

    # ---------- cabeçalho / rodapé ----------
    def nav(s, ativo):
        N = [('Início', 'index.html')]
        N.append(('Cardápio', 'cardapio.html'))
        if s.on.get('quiz'): N.append(('Quiz do burger' if False else 'Quiz', 'quiz.html'))
        casa = [('Nossa História', 'historia.html')]
        if s.on.get('como_fazemos'): casa.append(('Como fazemos', 'como-fazemos.html'))
        if s.on.get('unidades'): casa.append(('Unidades', 'unidades.html'))
        N.append(('A casa', casa))
        if s.on.get('eventos'): N.append(('Eventos', 'eventos.html'))
        if s.on.get('blog'): N.append(('Blog', 'blog.html'))
        N.append(('Contato', 'contato.html'))
        ACT = ' text-primary after:absolute after:inset-x-0 after:-bottom-1 after:h-0.5 after:bg-primary'
        LC = 'relative py-1 transition hover:text-primary'
        o = '<nav class="hidden items-center gap-6 text-sm lg:flex" aria-label="Principal">'
        for lab, h in N:
            if isinstance(h, list):
                on = ativo in [x for x, _ in h]
                o += '<div class="cb-dd"><button type="button" class="%s%s" aria-haspopup="true">%s <span aria-hidden="true">▾</span></button><div class="cb-dd-menu"><div>%s</div></div></div>' % (LC, ACT if on else '', lab, ''.join('<a href="%s" class="%s">%s</a>' % (u, 'text-primary' if x == ativo else '', x) for x, u in h))
            else:
                o += '<a href="%s" class="%s%s">%s</a>' % (h, LC, ACT if lab == ativo else '', lab)
        return o + '</nav>'
    def topo(s, ativo):
        M = s.M
        logo = ('<img src="%s" alt="" class="h-9 w-9 rounded-full object-cover">' % s.foto(M['logo'])) if M.get('logo') else s.ic('flame', 'h-5 w-5')
        nome2 = '<br/><span class="text-primary">%s</span>' % e(M['linha2']) if M.get('linha2') else ''
        aviso = ''
        if s.S.get('aviso_topo'):
            aviso = '<div class="relative bg-primary px-10 py-2 text-center text-xs font-semibold text-primary-foreground sm:text-sm"><span>%s</span>%s<button aria-label="Fechar aviso" class="absolute right-3 top-1/2 -translate-y-1/2">%s</button></div>' % (
                e(s.S['aviso_topo']),
                ('<a href="cardapio.html" class="ml-3 inline-flex items-center gap-1 rounded-full bg-ink px-3 py-1 text-ink-foreground">%s %s</a>' % (e(s.S['aviso_botao']), s.ic('arrow-right', 'h-3 w-3'))) if s.S.get('aviso_botao') else '',
                s.ic('x', 'h-4 w-4'))
        return aviso + '<header class="sticky top-0 z-40 bg-ink/95 text-ink-foreground backdrop-blur"><div class="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-4 sm:px-6"><a href="index.html" class="flex shrink-0 items-center gap-2" aria-label="%s — início"><span class="grid h-9 w-9 place-items-center rounded-full bg-primary text-primary-foreground">%s</span><span class="font-display text-xl leading-none">%s%s</span></a>%s<div class="flex items-center gap-1 sm:gap-3"><button aria-label="Buscar" class="rounded-full p-2 hover:text-primary">%s</button><button aria-label="Carrinho, 0 itens" class="relative rounded-full p-2 hover:text-primary">%s<span class="absolute -right-0.5 -top-0.5 grid h-5 min-w-5 place-items-center rounded-full bg-primary px-1 text-[10px] font-bold text-primary-foreground transition">0</span></button><a href="cardapio.html" class="btn btn-primary hidden !py-2 sm:inline-flex">Peça Online %s</a><button aria-label="Abrir menu" class="p-2 lg:hidden">%s</button></div></div></header>' % (
            e(M['nome']), logo, e(M['linha1']), nome2, s.nav(ativo), s.ic('search', 'h-5 w-5'), s.ic('shopping-bag', 'h-5 w-5'), s.ic('arrow-right', 'h-4 w-4'), s.ic('menu', 'h-6 w-6'))
    def rodape(s):
        K, M = s.K, s.M
        soc = ''
        for k, lab in (('instagram', 'Instagram'), ('facebook', 'Facebook'), ('youtube', 'YouTube')):
            if K.get(k): soc += '<a href="%s" target="_blank" rel="noopener" aria-label="%s" class="grid h-9 w-9 place-items-center rounded-full border border-ink-foreground/20 transition hover:border-primary hover:bg-primary hover:text-primary-foreground">%s</a>' % (e(K[k]), lab, s.ic(k, 'h-4 w-4'))
        li = lambda h, t: '<li><a href="%s" class="transition hover:text-primary">%s</a></li>' % (h, t)
        rap = li('index.html', 'Início') + li('cardapio.html', 'Cardápio') + li('historia.html', 'Nossa História')
        if s.on.get('quiz'): rap += li('quiz.html', 'Quiz')
        if s.on.get('como_fazemos'): rap += li('como-fazemos.html', 'Como fazemos')
        if s.on.get('unidades'): rap += li('unidades.html', 'Unidades')
        if s.on.get('eventos'): rap += li('eventos.html', 'Eventos')
        if s.on.get('blog'): rap += li('blog.html', 'Blog')
        info = ''
        if K.get('endereco_principal'): info += '<li class="flex gap-2">%s %s</li>' % (s.ic('map-pin', 'mt-0.5 h-4 w-4 shrink-0 text-primary'), e(K['endereco_principal']))
        if K.get('horario'): info += '<li class="flex gap-2">%s %s</li>' % (s.ic('clock', 'mt-0.5 h-4 w-4 shrink-0 text-primary'), e(K['horario']))
        if K.get('telefone'): info += '<li class="flex gap-2">%s %s</li>' % (s.ic('phone', 'mt-0.5 h-4 w-4 shrink-0 text-primary'), e(K['telefone']))
        nome2 = ' <span class="text-primary">%s</span>' % e(M['linha2']) if M.get('linha2') else ''
        return '<footer id="contato" class="bg-ink text-ink-foreground"><div class="mx-auto grid max-w-7xl gap-10 px-4 py-16 sm:grid-cols-2 sm:px-6 lg:grid-cols-4"><div><span class="flex items-center gap-2"><span class="grid h-9 w-9 place-items-center rounded-full bg-primary text-primary-foreground">%s</span><span class="font-display text-xl leading-none">%s%s</span></span><p class="mt-4 max-w-xs text-sm text-ink-muted">%s</p><div class="mt-5 flex gap-3">%s</div></div><div><h3 class="font-bold">Links rápidos</h3><ul class="mt-4 space-y-2 text-sm text-ink-muted">%s</ul></div><div><h3 class="font-bold">Suporte</h3><ul class="mt-4 space-y-2 text-sm text-ink-muted">%s%s%s</ul></div><div><h3 class="font-bold">Visite-nos</h3><ul class="mt-4 space-y-3 text-sm text-ink-muted">%s</ul></div></div><p class="border-t border-ink-foreground/10 py-6 text-center text-xs text-ink-muted">© %s %s. Todos os direitos reservados.</p></footer>' % (
            s.ic('flame', 'h-5 w-5'), e(M['linha1']), nome2, e(M['rodape']), soc, rap,
            li('contato.html#faq', 'Perguntas frequentes'), li('contato.html', 'Fale conosco'), li('politica.html', 'Privacidade e termos'), info, __import__('datetime').date.today().year, e(M['nome']))

    # ---------- documento ----------
    def head(s, titulo, desc, pagina, img=None, extra=''):
        M, S = s.M, s.S
        dom = S.get('dominio', '').rstrip('/')
        url = (dom + '/' + pagina) if dom else ''
        og = (dom + '/' + img) if (dom and img) else ''
        h = '<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>%s</title><meta name="description" content="%s">' % (e(titulo), e(desc))
        h += '<link rel="icon" href="favicon.svg" type="image/svg+xml"><link rel="icon" href="favicon.ico" sizes="any"><link rel="apple-touch-icon" href="apple-touch-icon.png">'
        if url: h += '<link rel="canonical" href="%s">' % e(url)
        h += '<meta property="og:title" content="%s"><meta property="og:description" content="%s"><meta property="og:type" content="website"><meta property="og:locale" content="pt_BR"><meta property="og:site_name" content="%s">' % (e(titulo), e(desc), e(M['nome']))
        if url: h += '<meta property="og:url" content="%s">' % e(url)
        if og: h += '<meta property="og:image" content="%s"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="%s">' % (e(og), e(og))
        fam = '&'.join('family=' + f.replace(' ', '+') for f in (M['fonte_titulo'], M['fonte_manuscrita']))
        h += '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?%s&family=Inter:wght@400;500;600;700;800&display=swap">' % fam
        h += '<link rel="stylesheet" href="base.css"><link rel="stylesheet" href="site.css"><link rel="stylesheet" href="tema.css">'
        return h + extra
    def scripts(s, extra=''):
        t = '<script src="config.js"></script><script src="site.js" defer></script>' + extra
        if s.cookies_on(): t += '<script src="cookies.js" defer></script>'
        return t
    def cookies_on(s): return bool(s.S.get('aviso_cookies') or s.S.get('analytics_id') or s.S.get('pixel_id'))
    def doc(s, pagina, titulo, desc, corpo, ativo, img=None, jsonld='', extra_head='', extra_js='', home=False):
        h = s.head(titulo, desc, pagina, img, jsonld + extra_head)
        inner = '<div class="min-h-screen overflow-x-hidden">' + s.topo(ativo) + corpo + s.rodape() + '</div>' + s.scripts(extra_js)
        if s.artefato and home: return h + inner
        return '<!doctype html><html lang="%s"><head>%s</head><body>%s</body></html>' % (s.S.get('idioma', 'pt-BR'), h, inner)
    def titulo_pg(s, t): return '%s — %s' % (t, s.M['nome'])

    # ---------- componentes ----------
    def hero(s, chave):
        p = s.C['paginas'][chave]
        return '<section class="cb-hero"><img src="%s" alt=""><div class="cb-wrap"><p class="cb-eyebrow">%s</p><h1 style="margin-top:.8rem">%s</h1><p class="lead">%s</p></div></section>' % (s.foto(p['foto']), e(p['eyebrow']), e(p['titulo']), e(p['texto']))
    def wrapsec(s, inner, cls=''): return '<section class="cb-section %s"><div class="cb-wrap">%s</div></section>' % (cls, inner)
    def cta(s):
        T = s.C['textos']
        return '<section class="cb-band"><div class="cb-wrap" style="padding-block:3.5rem;display:flex;flex-wrap:wrap;gap:1.5rem;align-items:center;justify-content:space-between"><div><h2 class="font-display" style="font-size:clamp(1.8rem,4vw,2.6rem);font-weight:400;text-transform:uppercase">%s</h2><p class="cb-muted" style="margin-top:.4rem">%s</p></div><a class="btn btn-primary" href="cardapio.html">%s</a></div></section>' % (e(T['cta_titulo']), e(T['cta_texto']), e(T['cta_botao']))
    def quizban(s):
        T = s.C['textos']
        return '<div class="cb-quizban"><div><p class="cb-eyebrow">%s</p><h2 class="font-display">%s</h2><p>%s</p></div><a class="btn btn-primary" href="quiz.html">%s</a></div>' % (e(T['quiz_chamada']), e(T['quiz_titulo']), e(T['quiz_texto']), e(T['quiz_botao']))
    def fld(s, l, t='text', extra=''): return '<label>%s<input type="%s" name="%s" %s></label>' % (e(l), t, e(l), extra)
    def mcard(s, m):
        return '<article class="cb-card"%s><a class="img" href="%s"><img src="%s" alt="%s" loading="lazy" width="640" height="480"></a><div class="body"><h3><a href="%s">%s</a></h3><p>%s</p><div class="row"><span class="cb-price">%s</span><button type="button" class="btn btn-primary cb-btn-sm" data-add="%s" aria-label="Adicionar %s ao carrinho">Adicionar +</button></div></div></article>' % (
            '', 'prato-%s.html' % m['id'], s.foto(m['foto']), e(m['nome']), 'prato-%s.html' % m['id'], e(m['nome']), e(m['descricao']), s.brl(m['preco']), m['id'], e(m['nome']))

    # ---------- páginas ----------
    def pg_home(s):
        C, H = s.C, s.C['hero']
        arrow = s.ic('arrow-right', 'h-4 w-4')
        ico = ['leaf', 'salad', 'heart', 'star']
        dest = ''.join('<div class="flex flex-col items-center text-center text-xs sm:items-start sm:text-left">%s<span class="font-semibold">%s</span><span class="text-ink-muted">%s</span></div>' % (s.ic(ico[i % 4], 'mb-2 h-5 w-5 text-primary'), e(a), e(b)) for i, (a, b) in enumerate(H['destaques']))
        tit = H['titulo']
        titulo = '<br/>'.join(e(t) for t in tit[:-1]) + ('<br/>' if len(tit) > 1 else '') + '<span class="text-primary">%s</span>' % e(tit[-1])
        hero = '<section id="inicio" class="relative overflow-hidden bg-ink text-ink-foreground"><img src="%s" alt="%s" width="1600" height="1008" class="absolute inset-0 h-full w-full object-cover object-right opacity-60 md:left-1/4 md:w-3/4 md:opacity-100" /><div class="absolute inset-0 bg-gradient-to-r from-ink via-ink/85 to-ink/10"></div><div class="relative mx-auto max-w-7xl px-4 py-20 sm:px-6 md:py-28"><div class="reveal max-w-xl" style="transition-delay:0ms"><p class="text-xs font-bold tracking-[0.25em] text-ink-muted">%s</p><h1 class="mt-4 font-display text-6xl leading-[0.95] sm:text-7xl lg:text-8xl">%s</h1><p class="mt-6 max-w-md text-ink-muted">%s</p><div class="mt-8 flex flex-wrap gap-3"><a href="cardapio.html" class="btn btn-primary">%s %s</a><a href="cardapio.html" class="btn btn-outline-light">%s</a></div></div>%s<div class="reveal mt-14 grid max-w-2xl grid-cols-2 gap-6 sm:grid-cols-4" style="transition-delay:200ms">%s</div></div></section>' % (
            s.foto(H['foto']), e(H['alt']), e(H['chamada']), titulo, e(H['texto']), e(H['botao1']), arrow, e(H['botao2']),
            ('<div class="pointer-events-none absolute right-[30%%] top-16 hidden rotate-[-6deg] text-ink-foreground lg:block"><p class="font-hand text-4xl leading-none">%s</p>%s</div>' % (H['nota'], s.ic('hand', 'ml-20 mt-1 h-14 w-20 text-primary'))) if H.get('nota') else '', dest)
        circ = ''.join('<a href="cardapio.html#cat-%s" class="group flex w-28 shrink-0 snap-start flex-col items-center gap-3 text-center"><span class="block h-28 w-28 overflow-hidden rounded-full bg-cream shadow-card ring-4 ring-transparent transition group-hover:ring-primary"><img src="%s" alt="%s" loading="lazy" width="224" height="224" class="h-full w-full object-cover transition duration-500 group-hover:scale-110"/></span><span class="text-sm font-semibold">%s</span></a>' % (c['id'], s.foto(c['foto']), e(c['nome']), e(c['nome'])) for c in C['categorias'])
        cats = '<section id="cardapio" class="mx-auto max-w-7xl px-4 pt-20 sm:px-6"><div class="reveal flex items-end justify-between gap-4"><div><p class="label-red">Explore o cardápio</p><h2 class="mt-2 text-3xl font-extrabold tracking-tight sm:text-4xl">Algo para cada vontade</h2></div><a href="cardapio.html" class="hidden shrink-0 items-center gap-1 text-sm font-semibold hover:text-brand-red sm:flex">Ver cardápio completo %s</a></div><div class="reveal no-scrollbar -mx-4 mt-10 flex snap-x gap-6 overflow-x-auto px-4 pb-4 md:mx-0 md:justify-between md:px-0">%s</div></section>' % (arrow, circ)
        cards = ''
        for i, pid in enumerate(C['mais_vendidos']):
            m = s.byid[pid]
            badge = ('<span class="absolute right-3 top-3 rounded-md bg-brand-red px-2 py-1 text-[11px] font-bold text-ink-foreground">%s</span>' % e(m['etiquetas'][0])) if m.get('etiquetas') else ''
            cards += '<div class="reveal w-[78%%] shrink-0 snap-start sm:w-[45%%] lg:w-[calc(25%%-15px)]" style="transition-delay:%dms"><article class="group h-full overflow-hidden rounded-2xl bg-card shadow-card transition duration-300 hover:-translate-y-1 hover:shadow-lift"><a href="prato-%s.html" class="relative block aspect-[4/3] overflow-hidden bg-ink"><img src="%s" alt="%s" loading="lazy" width="944" height="704" class="h-full w-full object-cover transition duration-500 group-hover:scale-105" />%s</a><div class="p-5"><h3 class="font-bold"><a href="prato-%s.html">%s</a></h3><p class="mt-1 text-sm text-muted-foreground">%s</p><div class="mt-4 flex items-center justify-between"><span class="text-lg font-extrabold">%s</span><button class="btn btn-primary !px-4 !py-2 !text-sm" aria-label="Adicionar %s ao carrinho" data-add="%s">Adicionar %s</button></div></div></article></div>' % (i * 80, m['id'], s.foto(m['foto']), e(m['nome']), badge, m['id'], e(m['nome']), e(m['descricao']), s.brl(m['preco']), e(m['nome']), m['id'], s.ic('plus', 'h-4 w-4'))
        btns = '<div class="flex gap-2"><button aria-label="Anterior" class="grid h-10 w-10 place-items-center rounded-full border border-border bg-card transition hover:bg-primary hover:border-primary">%s</button><button aria-label="Próximo" class="grid h-10 w-10 place-items-center rounded-full border border-border bg-card transition hover:bg-primary hover:border-primary">%s</button></div>' % (s.ic('arrow-left', 'h-4 w-4'), arrow)
        mv = '<section id="mais-vendidos" class="mx-auto max-w-7xl px-4 py-20 sm:px-6"><div class="reveal flex items-end justify-between"><div><p class="label-red">Favoritos dos clientes</p><h2 class="mt-2 text-3xl font-extrabold tracking-tight sm:text-4xl">Mais vendidos</h2></div>%s</div><div class="no-scrollbar -mx-4 mt-10 flex snap-x snap-mandatory gap-5 overflow-x-auto px-4 pb-6">%s</div></section>' % (btns, cards)
        P1, P2 = C['promo1'], C['promo2']
        promos = '<section id="combos" class="grid md:grid-cols-2"><div class="relative flex min-h-[360px] items-center overflow-hidden bg-ink text-ink-foreground"><img src="%s" alt="%s" loading="lazy" class="absolute inset-0 h-full w-full object-cover object-right opacity-90" /><div class="absolute inset-0 bg-gradient-to-r from-ink via-ink/70 to-transparent"></div><div class="reveal relative p-8 sm:p-12"><h2 class="font-display text-5xl leading-none sm:text-6xl">%s<br/><span class="text-primary">%s</span></h2><p class="mt-4 max-w-[14rem] text-ink-muted">%s</p><a href="%s" class="btn btn-primary mt-6">%s %s</a></div></div><div class="relative flex min-h-[360px] items-center overflow-hidden bg-cream"><img src="%s" alt="%s" loading="lazy" class="absolute right-0 top-0 h-full w-1/2 object-cover" /><div class="reveal relative p-8 sm:p-12"><h2 class="font-display text-5xl leading-none sm:text-6xl">%s<br/>%s</h2><p class="mt-1 font-hand text-2xl text-brand-red">%s</p><p class="mt-3 max-w-[13rem] text-sm text-muted-foreground">%s</p><a href="%s" class="btn btn-outline-dark mt-6">%s %s</a></div>%s</div></section>' % (
            s.foto(P1['foto']), e(P1['alt']), e(P1['titulo'][0]), e(P1['titulo'][1]), e(P1['texto']), e(P1['link']), e(P1['botao']), arrow,
            s.foto(P2['foto']), e(P2['alt']), e(P2['titulo'][0]), e(P2['titulo'][1]), e(P2['sub']), e(P2['texto']), e(P2['link']), e(P2['botao']), arrow,
            ('<p class="absolute right-6 top-6 hidden rotate-[8deg] font-hand text-2xl leading-tight sm:block">%s</p>' % P2['nota']) if P2.get('nota') else '')
        fi = ['flame', 'award', 'sofa', 'users']
        dif = '<section class="mx-auto max-w-7xl px-4 py-14 sm:px-6"><div class="grid grid-cols-2 gap-y-10 lg:grid-cols-4 lg:divide-x lg:divide-border">%s</div></section>' % ''.join('<div class="reveal flex flex-col items-center px-4 text-center"><span class="grid h-14 w-14 place-items-center rounded-full bg-primary/20 text-brand-red">%s</span><h3 class="mt-3 font-bold">%s</h3><p class="text-xs text-muted-foreground">%s</p></div>' % (s.ic(fi[i % 4], 'h-6 w-6'), e(a), e(b)) for i, (a, b) in enumerate(C['diferenciais']))
        HH = C['home_historia']
        hist = '<section id="historia" class="grid md:grid-cols-2"><img src="%s" alt="%s" loading="lazy" class="h-72 w-full object-cover md:h-full" /><div class="relative bg-cream p-8 sm:p-14 lg:p-20"><div class="reveal"><p class="label-red">%s</p><h2 class="mt-3 text-4xl font-extrabold leading-tight tracking-tight">%s<br/>%s</h2><p class="mt-5 max-w-md text-muted-foreground">%s</p><a href="historia.html" class="btn btn-primary mt-8">%s %s</a></div>%s</div></section>' % (
            s.foto(HH['foto']), e(HH['alt']), e(HH['rotulo']), e(HH['titulo'][0]), e(HH['titulo'][1]), e(HH['texto']), e(HH['botao']), arrow,
            ('<div class="mt-10 flex items-center gap-3 lg:absolute lg:right-10 lib:top-12 lg:mt-0 lg:flex-col"><p class="rotate-[-4deg] font-hand text-3xl leading-tight">%s</p>%s</div>' % (HH['nota'], s.ic('burger', 'h-10 w-10'))).replace('lib:', 'lg:') if HH.get('nota') else '')
        dep = ''
        D = C['depoimentos']
        if D.get('itens'):
            fig = ''.join('<figure class="w-[85%%] shrink-0 snap-start rounded-2xl bg-card p-6 shadow-card sm:w-[calc(50%%-10px)] lg:w-[calc(33.333%%-14px)]"><blockquote class="text-sm leading-relaxed">“%s”</blockquote><figcaption class="mt-6 flex items-center justify-between gap-3"><span class="flex items-center gap-3"><span class="grid h-10 w-10 place-items-center rounded-full bg-primary text-xs font-bold text-primary-foreground" aria-hidden="true">%s</span><span class="text-sm font-semibold">%s</span></span><span class="flex text-primary" aria-label="5 de 5 estrelas">%s</span></figcaption></figure>' % (e(i['texto']), e(''.join(w[0] for w in i['nome'].split()[:2]).upper()), e(i['nome']), s.ic('star', 'h-4 w-4 fill-current') * 5) for i in D['itens'])
            dep = '<section id="depoimentos" class="mx-auto max-w-7xl px-4 py-20 sm:px-6"><div class="reveal flex items-end justify-between"><div><p class="label-red">%s</p><h2 class="mt-2 text-3xl font-extrabold tracking-tight sm:text-4xl">%s</h2></div>%s</div><div class="no-scrollbar -mx-4 mt-10 flex snap-x snap-mandatory gap-5 overflow-x-auto px-4 pb-6">%s</div></section>' % (e(D['rotulo']), e(D['titulo']), btns, fig)
        steps = ''
        if s.on.get('como_fazemos'):
            steps = '<section class="cb-section"><div class="cb-wrap"><div class="reveal" style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:end;gap:1rem"><div><p class="cb-red">Como fazemos</p><h2 class="cb-h2">%s</h2></div><a href="como-fazemos.html" class="font-semibold hover:text-brand-red" style="font-size:.9rem">Ver o passo a passo →</a></div><div class="cb-grid reveal" style="margin-top:2rem;grid-template-columns:repeat(auto-fit,minmax(min(100%%,14rem),1fr))">%s</div></div></section>' % (e(s.C['paginas']['como_fazemos']['titulo'].capitalize()), ''.join('<a href="como-fazemos.html#%s" class="cb-step"><span class="cb-red">%s</span><h3 class="font-display">%s</h3><p>%s</p></a>' % (c['id'], e(c['cap']), e(c['titulo']), e(c['gancho'])) for c in C['como_fazemos']['capitulos']))
        qz = '<section class="cb-section" style="padding-block:0 4rem"><div class="cb-wrap reveal">%s</div></section>' % s.quizban() if s.on.get('quiz') else ''
        blog = ''
        if s.on.get('blog'):
            blog = '<section class="cb-section"><div class="cb-wrap"><div class="reveal" style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:end;gap:1rem"><div><p class="cb-red">Blog</p><h2 class="cb-h2">Direto da cozinha</h2></div><a href="blog.html" class="font-semibold hover:text-brand-red" style="font-size:.9rem">Ver todos →</a></div><div class="cb-grid reveal" style="margin-top:2rem">%s</div></div></section>' % ''.join('<a href="post-%s.html" class="cb-card"><div class="img"><img src="%s" alt="" loading="lazy"></div><div class="body"><div class="cb-post-meta"><span class="cb-pill">%s</span><span>%s</span></div><h3>%s</h3></div></a>' % (p['slug'], s.foto(p['foto']), e(p['categoria']), e(p['data']), e(p['titulo'])) for p in C['blog'][:3])
        W = C['chamada_whatsapp']
        wa = '<section class="relative overflow-hidden bg-ink text-ink-foreground">%s%s<div class="relative mx-auto flex max-w-5xl flex-col items-center gap-6 px-6 py-14 md:flex-row md:justify-between md:px-32"><div class="text-center md:text-left"><h2 class="text-2xl font-extrabold sm:text-3xl">%s</h2><p class="mt-1 text-sm text-ink-muted">%s</p></div><a class="btn btn-primary" target="_blank" rel="noopener" href="https://wa.me/%s?text=%s">%s</a></div></section>' % (
            ('<img src="%s" alt="" aria-hidden="true" loading="lazy" class="absolute -left-16 top-1/2 hidden h-56 w-56 -translate-y-1/2 rounded-full object-cover md:block" />' % s.foto(W['foto1'])) if W.get('foto1') else '',
            ('<img src="%s" alt="" aria-hidden="true" loading="lazy" class="absolute -right-16 top-1/2 hidden h-56 w-56 -translate-y-1/2 rounded-full object-cover md:block" />' % s.foto(W['foto2'])) if W.get('foto2') else '',
            e(W['titulo']), e(W['texto']), s.K['whatsapp'], __import__('urllib.parse').parse.quote(W['mensagem']), e(W['botao']))
        corpo = hero + cats + mv + promos + dif + hist + steps + qz + dep + blog + wa
        return s.doc('index.html', '%s — %s' % (s.M['nome'], s.M['slogan']), s.M['descricao'], corpo, 'Início', img=s.foto(H['foto']), jsonld=s.jsonld(), home=True)

    def jsonld(s):
        M, K = s.M, s.K
        d = {'@context': 'https://schema.org', '@type': 'Restaurant', 'name': M['nome'], 'description': M['descricao'], 'servesCuisine': M.get('culinaria', 'Hambúrgueres'), 'telephone': K.get('telefone', ''), 'hasMenu': (s.S['dominio'].rstrip('/') + '/cardapio.html') if s.S.get('dominio') else 'cardapio.html'}
        if s.S.get('dominio'): d['url'] = s.S['dominio']; d['image'] = s.S['dominio'].rstrip('/') + '/' + s.foto(s.C['hero']['foto'])
        if K.get('endereco_principal'): d['address'] = {'@type': 'PostalAddress', 'streetAddress': K['endereco_principal'], 'addressCountry': 'BR'}
        if K.get('horario_estruturado'): d['openingHours'] = K['horario_estruturado']
        same = [K[k] for k in ('instagram', 'facebook', 'youtube') if K.get(k)]
        if same: d['sameAs'] = same
        return '<script type="application/ld+json">%s</script>' % json.dumps(d, ensure_ascii=False)

    def pg_cardapio(s):
        C = s.C
        n = lambda cid: len([p for p in s.pratos if p['categoria'] == cid])
        chips = ''.join('<button type="button" class="cb-chip" data-to="#cat-%s">%s <small>%d</small></button>' % (c['id'], e(c['nome']), n(c['id'])) for c in C['categorias'] if n(c['id']))
        tags = '<div class="cb-wrap cb-tagrow"><span class="cb-muted">Perfil:</span>%s</div>' % ''.join('<button type="button" class="cb-tag" data-tag="%s" aria-pressed="false">%s</button>' % (e(t), e(t)) for t in C['filtros_perfil'])
        secs = ''
        for c in C['categorias']:
            its = [p for p in s.pratos if p['categoria'] == c['id']]
            if not its: continue
            cards = ''.join(s.mcard(m).replace('<article class="cb-card"', '<article class="cb-card" id="item-%s" data-tags="%s" data-s="%s"' % (m['id'], e(','.join(m.get('etiquetas', []))), e((m['nome'] + ' ' + m['descricao'] + ' ' + c['nome']).lower())), 1) for m in its)
            secs += '<section class="cb-cat" id="cat-%s"><h2>%s <small>%d %s</small></h2><div class="cb-grid">%s</div></section>' % (c['id'], e(c['nome']), len(its), 'item' if len(its) == 1 else 'itens', cards)
        corpo = s.hero('cardapio') + '<div class="cb-chips"><div class="cb-wrap">%s<input id="menu-q" class="cb-search" type="search" placeholder="Buscar prato" aria-label="Buscar prato"></div>%s</div>' % (chips, tags if C['filtros_perfil'] else '') + '<div class="cb-wrap" style="padding-bottom:4rem">%s<p class="cb-empty" id="menu-empty" hidden>Nenhum prato encontrado para esse filtro.</p>%s</div>' % (secs, ('<div style="margin-top:3rem">%s</div>' % s.quizban()) if s.on.get('quiz') else '')
        p = C['paginas']['cardapio']
        return {'cardapio.html': s.doc('cardapio.html', s.titulo_pg('Cardápio'), p['texto'], corpo, 'Cardápio', img=s.foto(p['foto']))}

    def pg_pratos(s):
        o = {}
        DEFS = {'Suculência': 'Quanto suco o blend solta a cada mordida.', 'Crocância': 'Textura da casca, do empanado ou da fritura.', 'Defumado': 'Presença de bacon e molho defumado.', 'Picância': 'Nível de ardência. 1 é suave, 5 é forte.', 'Sal': 'Intensidade do tempero.', 'Cremosidade': 'Corpo de queijo, sorvete ou molho.', 'Frescor': 'Vegetais e molhos frescos no conjunto.', 'Doçura': 'Quanto de açúcar o prato leva.'}
        for m in s.pratos:
            cat = s.cats.get(m['categoria'], {'nome': '', 'id': ''})
            tags = ''.join('<span class="cb-pill">%s</span>' % e(t) for t in m.get('etiquetas', []))
            bars = ''.join('<div class="cb-attr"><div><b>%s</b><small>%s</small></div><div class="cb-seg5" role="img" aria-label="%d de 5">%s</div><span>%d/5</span></div>' % (e(a), e(DEFS.get(a, '')), v, ''.join('<i class="%s"></i>' % ('on' if k < v else '') for k in range(5)), v) for a, v in m.get('perfil', []))
            perfil = ('<section class="cb-section cb-cream"><div class="cb-wrap"><p class="cb-red">Perfil do prato</p><h2 class="cb-h2">O que esperar da mordida</h2><div class="cb-attrs">%s</div></div></section>' % bars) if bars else ''
            cont = ('<div style="margin-top:1.4rem"><b style="font-size:.85rem">Contém</b><div class="cb-pills">%s</div><p class="cb-muted" style="font-size:.78rem;margin-top:.5rem">Confirme alérgenos com a equipe antes de pedir.</p></div>' % ''.join('<span class="cb-pill alt">%s</span>' % e(a) for a in m['contem'])) if m.get('contem') else ''
            comb = [s.byid[p] for p in m.get('combina', []) if p in s.byid]
            rel = s.wrapsec('<p class="cb-red">Combina com</p><h2 class="cb-h2" style="margin-bottom:1.5rem">Peça junto</h2><div class="cb-grid">%s</div>' % ''.join(s.mcard(x) for x in comb)) if comb else ''
            info = '<div><a class="cb-red" href="cardapio.html#cat-%s">← %s</a><div class="cb-pills" style="margin-top:.8rem">%s</div><h1 class="font-display" style="font-size:clamp(2.4rem,6vw,4rem);line-height:1;font-weight:400;text-transform:uppercase;margin-top:.6rem;text-wrap:balance">%s</h1><p class="cb-price" style="font-size:1.8rem;margin-top:.8rem">%s</p><p class="cb-prose" style="line-height:1.7;margin-top:1rem;max-width:34rem">%s</p>%s<div class="cb-actions"><button type="button" class="btn btn-primary" data-add="%s" aria-label="Adicionar %s ao carrinho">Adicionar ao carrinho +</button><a class="btn btn-outline-dark" href="cardapio.html">Ver cardápio</a></div></div>' % (cat['id'], e(cat['nome']), tags, e(m['nome']), s.brl(m['preco']), e(m.get('descricao_longa') or m['descricao']), cont, m['id'], e(m['nome']))
            corpo = s.wrapsec('<div class="cb-split"><img src="%s" alt="%s">%s</div>' % (s.foto(m['foto']), e(m['nome']), info)) + perfil + rel
            f = 'prato-%s.html' % m['id']
            o[f] = s.doc(f, s.titulo_pg(m['nome']), m.get('descricao_longa') or m['descricao'], corpo, 'Cardápio', img=s.foto(m['foto']))
        return o

    def pg_historia(s):
        Hh = s.C['historia']
        corpo = s.hero('historia') + s.wrapsec('<div class="cb-split"><div class="cb-prose"><p class="cb-red">%s</p><h2 class="cb-h2">%s</h2>%s<div class="cb-actions"><a class="btn btn-primary" href="cardapio.html">Ver cardápio</a>%s</div></div><img src="%s" alt="%s" loading="lazy"></div>' % (e(Hh['rotulo']), e(Hh['titulo']), ''.join('<p>%s</p>' % e(p) for p in Hh['paragrafos']), '<a class="btn btn-outline-dark" href="unidades.html">Conhecer as unidades</a>' if s.on.get('unidades') else '', s.foto(Hh['foto']), e(Hh['alt']))) + s.wrapsec('<p class="cb-red">O que vai no lanche</p><h2 class="cb-h2" style="margin-bottom:1.5rem">%s</h2><div class="cb-feat">%s</div>' % (e(Hh['pilares_titulo']), ''.join('<div><h3>%s</h3><p>%s</p></div>' % (e(a), e(b)) for a, b in Hh['pilares'])), 'cb-cream') + s.cta()
        p = s.C['paginas']['historia']
        return {'historia.html': s.doc('historia.html', s.titulo_pg('Nossa História'), p['texto'], corpo, 'Nossa História', img=s.foto(p['foto']))}

    def pg_unidades(s):
        uc = ''.join('<article class="cb-card"><div class="body" style="padding:1.5rem"><p class="cb-red">Unidade</p><h3 style="font-size:1.5rem">%s</h3><ul class="cb-info"><li><b>Endereço</b><span>%s</span></li><li><b>Horário</b><span>%s</span></li><li><b>Telefone</b><span>%s</span></li></ul><div class="cb-actions"><a class="btn btn-primary cb-btn-sm" target="_blank" rel="noopener" href="https://www.google.com/maps/search/?api=1&amp;query=%s">Como chegar</a><a class="btn btn-outline-dark cb-btn-sm" href="cardapio.html">Pedir agora</a></div></div></article>' % (e(u['nome']), e(u['endereco']), e(u['horario']), e(u['telefone']), __import__('urllib.parse').parse.quote_plus(u['endereco'])) for u in s.C['unidades'])
        corpo = s.hero('unidades') + s.wrapsec('<div class="cb-grid" style="grid-template-columns:repeat(auto-fit,minmax(min(100%%,19rem),1fr))">%s</div>' % uc) + s.cta()
        p = s.C['paginas']['unidades']
        return {'unidades.html': s.doc('unidades.html', s.titulo_pg('Unidades'), p['texto'], corpo, 'Unidades', img=s.foto(p['foto']))}

    def pg_eventos(s):
        Ev = s.C['eventos']
        tabs = '<div class="cb-tabs" role="tablist">%s</div>' % ''.join('<button type="button" role="tab" class="cb-chip%s" data-tab="%d" aria-selected="%s">%s</button>' % (' on' if k == 0 else '', k, 'true' if k == 0 else 'false', e(n)) for k, n in enumerate(Ev['pacotes']))
        panes = ''.join('<div class="cb-pane" data-pane="%d" role="tabpanel"%s><p style="font-weight:700;font-size:1.1rem;margin-bottom:1rem">%s</p><ul class="cb-checks">%s</ul></div>' % (k, '' if k == 0 else ' hidden', e(v[0]), ''.join('<li>%s</li>' % e(i) for i in v[1])) for k, (n, v) in enumerate(Ev['pacotes'].items()))
        hero = s.hero('eventos').replace('</p></div></section>', '</p><div class="cb-actions"><a class="btn btn-primary" href="#orcamento">Quero um orçamento</a><a class="btn btn-outline-light" href="#pacotes">Ver pacotes</a></div></div></section>')
        opts = ''.join('<option>%s</option>' % e(t) for t in Ev['tipos'])
        corpo = hero + s.wrapsec('<div class="cb-feat">%s</div>' % ''.join('<div><h3>%s</h3><p>%s</p></div>' % (e(a), e(b)) for a, b in Ev['beneficios'])) + '<section class="cb-section cb-cream" id="pacotes"><div class="cb-wrap"><p class="cb-red">Pacotes</p><h2 class="cb-h2" style="margin-bottom:1.5rem">Escolha o tipo de evento</h2>%s<div class="cb-panebox">%s</div></div></section>' % (tabs, panes) + s.wrapsec('<div class="cb-split" style="align-items:start"><div class="cb-prose"><p class="cb-red">Orçamento</p><h2 class="cb-h2" id="orcamento">Conte o que você tem em mente</h2><p>Preencha os dados ao lado. Montamos a mensagem e você a envia pelo WhatsApp para a nossa equipe.</p><ul class="cb-info"><li><b>Atendimento</b><span>%s</span></li><li><b>Resposta</b><span>%s</span></li></ul></div><div><form class="cb-form" data-wa="Orçamento de evento">%s%s<label>Tipo de evento<select name="Tipo de evento">%s</select></label>%s%s<label class="full">Detalhes<textarea name="Detalhes" placeholder="Local, restrições alimentares, horário"></textarea></label><button class="btn btn-primary full" type="submit">Montar mensagem</button></form><div class="cb-result" hidden></div></div></div>' % (e(Ev['atendimento']), e(Ev['resposta']), s.fld('Nome', 'text', 'required autocomplete="name"'), s.fld('Telefone', 'tel', 'autocomplete="tel"'), opts, s.fld('Convidados', 'number', 'min="1" inputmode="numeric"'), s.fld('Data', 'date'))) + s.cta()
        p = s.C['paginas']['eventos']
        return {'eventos.html': s.doc('eventos.html', s.titulo_pg('Eventos'), p['texto'], corpo, 'Eventos', img=s.foto(p['foto']))}

    def pg_blog(s):
        B = s.C['blog']; o = {}
        f = B[0]
        feat = '<a href="post-%s.html" class="cb-feature"><img src="%s" alt=""><div><span class="cb-pill">%s</span><h2 class="font-display">%s</h2><p>%s</p><span class="cb-red">Ler artigo</span></div></a>' % (f['slug'], s.foto(f['foto']), e(f['categoria']), e(f['titulo']), e(f['resumo']))
        bc = ''.join('<a href="post-%s.html" class="cb-card" data-f="%s"><div class="img"><img src="%s" alt="" loading="lazy"></div><div class="body"><div class="cb-post-meta"><span class="cb-pill">%s</span><span>%s</span></div><h3>%s</h3><p>%s</p></div></a>' % (p['slug'], e(p['categoria']), s.foto(p['foto']), e(p['categoria']), e(p['data']), e(p['titulo']), e(p['resumo'])) for p in B[1:])
        fch = '<div class="cb-tabs">%s</div>' % ''.join('<button type="button" class="cb-chip%s" data-fil="%s">%s</button>' % (' on' if k == 0 else '', e(x), e(x)) for k, x in enumerate(['Todos'] + s.C['blog_categorias']))
        corpo = s.hero('blog') + s.wrapsec(feat + '<div style="margin-top:2.5rem">%s</div><div class="cb-grid" id="posts" style="margin-top:1.5rem">%s</div>' % (fch, bc)) + s.cta()
        p = s.C['paginas']['blog']
        o['blog.html'] = s.doc('blog.html', s.titulo_pg('Blog'), p['texto'], corpo, 'Blog', img=s.foto(p['foto']))
        for p in B:
            rel = [r for r in B if r['slug'] != p['slug']][:2]
            more = '<div class="cb-grid" style="margin-top:1.2rem">%s</div>' % ''.join('<a href="post-%s.html" class="cb-card"><div class="body"><span class="cb-red">%s</span><h3>%s</h3></div></a>' % (r['slug'], e(r['categoria']), e(r['titulo'])) for r in rel)
            corpo = '<section class="cb-section"><div class="cb-wrap"><article class="cb-article"><a class="cb-red" href="blog.html">← Voltar ao blog</a><div class="cb-post-meta" style="margin-top:1rem"><span class="cb-pill">%s</span><span>%s</span></div><h1 class="font-display" style="font-size:clamp(2.2rem,6vw,3.5rem);line-height:1.02;margin-top:.8rem;font-weight:400;text-transform:uppercase;text-wrap:balance">%s</h1><p class="cb-muted" style="margin-top:.8rem">%s</p><img src="%s" alt="">%s<div class="cb-actions"><a class="btn btn-primary" href="cardapio.html">Ver cardápio</a></div><h2>Continue lendo</h2>%s</article></div></section>' % (e(p['categoria']), e(p['data']), e(p['titulo']), e(p['resumo']), s.foto(p['foto']), ''.join('<p>%s</p>' % e(x) for x in p['paragrafos']), more)
            fn = 'post-%s.html' % p['slug']
            o[fn] = s.doc(fn, s.titulo_pg(p['titulo']), p['resumo'], corpo, 'Blog', img=s.foto(p['foto']))
        return o

    def pg_como(s):
        CF = s.C['como_fazemos']; ch = CF['capitulos']
        sub = '<div class="cb-chips"><div class="cb-wrap">%s</div></div>' % ''.join('<button type="button" class="cb-chip" data-to="#%s">%s</button>' % (c['id'], e(c['titulo'])) for c in ch)
        body = ''.join('<section class="cb-cat cb-chap" id="%s"><div class="cb-split %s"><div class="cb-prose"><p class="cb-red">%s</p><h2 class="cb-h2">%s</h2><p style="font-weight:700;font-size:1.15rem">%s</p><p>%s</p></div><img src="%s" alt="" loading="lazy"></div></section>' % (c['id'], 'rev' if k % 2 else '', e(c['cap']), e(c['titulo']), e(c['gancho']), e(c['texto']), s.foto(c['foto'])) for k, c in enumerate(ch))
        comp = s.wrapsec('<p class="cb-red">Nossos compromissos</p><h2 class="cb-h2" style="margin-bottom:1.5rem">%s</h2><div class="cb-feat">%s</div><div class="cb-actions">%s<a class="btn btn-outline-dark" href="cardapio.html">Ver cardápio</a></div>' % (e(CF['compromissos_titulo']), ''.join('<div><h3>%s</h3><p>%s</p></div>' % (e(a), e(b)) for a, b in CF['compromissos']), '<a class="btn btn-primary" href="quiz.html">%s</a>' % e(s.C['textos']['quiz_titulo']) if s.on.get('quiz') else ''), 'cb-cream')
        corpo = s.hero('como_fazemos') + sub + '<div class="cb-wrap">%s</div>' % body + comp
        p = s.C['paginas']['como_fazemos']
        return {'como-fazemos.html': s.doc('como-fazemos.html', s.titulo_pg('Como fazemos'), p['texto'], corpo, 'Como fazemos', img=s.foto(p['foto']))}

    def pg_quiz(s):
        corpo = s.hero('quiz') + s.wrapsec('<div id="quiz" class="cb-quiz" aria-live="polite"></div>') + s.cta()
        p = s.C['paginas']['quiz']
        return {'quiz.html': s.doc('quiz.html', s.titulo_pg('Quiz'), p['texto'], corpo, 'Quiz', img=s.foto(p['foto']), extra_js='<script src="quiz-data.js"></script><script src="quiz.js" defer></script>')}

    def pg_contato(s):
        K = s.C['contato']
        fq = ''.join('<details><summary>%s</summary><p>%s</p></details>' % (e(a), e(b)) for a, b in s.C['faq'])
        info = ''.join('<li><b>%s</b><span>%s</span></li>' % (a, e(v)) for a, v in (('Telefone', K.get('telefone')), ('Horário', K.get('horario')), ('Endereço', K.get('endereco_principal')), ('E-mail', K.get('email'))) if v)
        assuntos = ''.join('<option>%s</option>' % a for a in ('Dúvida', 'Pedido', 'Elogio ou sugestão', 'Reclamação'))
        corpo = s.hero('contato') + s.wrapsec('<div class="cb-split" style="align-items:start"><div><p class="cb-red">Mensagem</p><h2 class="cb-h2" style="margin-bottom:1.2rem">Escreva para %s</h2><form class="cb-form" data-wa="Contato pelo site">%s%s<label class="full">Assunto<select name="Assunto">%s</select></label><label class="full">Mensagem<textarea name="Mensagem" required></textarea></label><button class="btn btn-primary full" type="submit">Montar mensagem</button></form><div class="cb-result" hidden></div></div><div><p class="cb-red">Onde estamos</p><ul class="cb-info" style="font-size:1rem">%s</ul>%s<h2 class="cb-h2" id="faq" style="margin-top:2.5rem">Perguntas frequentes</h2><div class="cb-faq" style="margin-top:.8rem">%s</div></div></div>' % (e(s.M['nome']), s.fld('Nome', 'text', 'required autocomplete="name"'), s.fld('E-mail', 'email', 'autocomplete="email"'), assuntos, info, '<div class="cb-actions"><a class="btn btn-outline-dark" href="unidades.html">Ver todas as unidades</a></div>' if s.on.get('unidades') else '', fq))
        p = s.C['paginas']['contato']
        return {'contato.html': s.doc('contato.html', s.titulo_pg('Contato'), p['texto'], corpo, 'Contato', img=s.foto(p['foto']))}

    def pg_politica(s):
        M, K = s.M, s.K
        medicao = ''
        if s.S.get('analytics_id') or s.S.get('pixel_id'):
            medicao = '<p>Com a sua autorização no aviso de cookies, usamos ferramentas de medição de visitas (%s) para entender como o site é usado e melhorar a experiência. Você pode recusar, e o site continua funcionando normalmente.</p>' % ', '.join(x for x, v in (('Google Analytics', s.S.get('analytics_id')), ('Meta Pixel', s.S.get('pixel_id'))) if v)
        contato = ' / '.join(x for x in (K.get('email'), K.get('telefone')) if x)
        corpo = s.hero('politica') + s.wrapsec('<div class="cb-article"><h2 id="privacidade" style="margin-top:0">Política de privacidade</h2><p><b>Responsável:</b> %s. Contato: %s.</p><p>Este site guarda no seu navegador apenas o conteúdo do carrinho, para que ele continue o mesmo entre as páginas. Esses dados ficam no seu aparelho.</p><p>Os dados que você digita nos formulários e no carrinho (nome, endereço, telefone, pedido) só saem do seu aparelho quando você decide enviar a mensagem pelo WhatsApp. Eles são usados apenas para atender o pedido ou responder a sua mensagem.</p>%s<p>Você pode pedir informações, correção ou exclusão dos seus dados pelo contato acima, conforme a Lei Geral de Proteção de Dados (LGPD).</p><h2 id="termos">Termos de uso</h2><p>Preços, itens e disponibilidade podem mudar sem aviso. O pedido só é confirmado depois que a equipe responder no WhatsApp. As imagens são ilustrativas. Informações de alérgenos são orientativas: confirme com a equipe antes de pedir.</p></div>' % (e(M['nome']), e(contato), medicao))
        p = s.C['paginas']['politica']
        return {'politica.html': s.doc('politica.html', s.titulo_pg('Privacidade e termos'), p['texto'], corpo, '', img=s.foto(p['foto']))}

    def pg_404(s):
        corpo = s.wrapsec('<div style="text-align:center;padding-block:4rem"><p class="cb-red">Erro 404</p><h1 class="font-display" style="font-size:clamp(2.5rem,7vw,4.5rem);font-weight:400;text-transform:uppercase;margin-top:.5rem">Essa página não existe</h1><p class="cb-muted" style="margin-top:1rem">Talvez o link tenha mudado. Volte para o início ou veja o cardápio.</p><div class="cb-actions" style="justify-content:center"><a class="btn btn-primary" href="index.html">Início</a><a class="btn btn-outline-dark" href="cardapio.html">Cardápio</a></div></div>')
        return {'404.html': s.doc('404.html', s.titulo_pg('Página não encontrada'), 'Página não encontrada', corpo, '')}

    # ---------- arquivos de apoio ----------
    def escrever_apoio(s):
        C, M, S, K = s.C, s.M, s.S, s.K
        for f in ('site.css', 'site.js', 'quiz.js', 'favicon.ico', 'favicon.svg', 'apple-touch-icon.png'): shutil.copy(MOD / f, s.out / f)
        shutil.copy(MOD / 'base.css', s.out / 'base.css')
        tema = ':root{--primary:%s;--primary-foreground:%s;--ring:%s;--ink:%s;--cream:%s;--brand-red:%s;--font-display:"%s",sans-serif;--font-hand:"%s",cursive}\nbody{background:var(--background)}\n' % (M['cor_destaque'], M['cor_sobre_destaque'], M['cor_destaque'], M['cor_escura'], M['cor_clara'], M['cor_vermelha'], M['fonte_titulo'], M['fonte_manuscrita'])
        open(s.out / 'tema.css', 'w').write(tema)
        menu = []
        for p in s.pratos:
            c = s.cats.get(p['categoria'], {'nome': ''})
            menu.append(dict(id=p['id'], cat=p['categoria'], catName=c['nome'], name=p['nome'], price=p['preco'], img='fotos/' + p['foto'], desc=p['descricao'], url='prato-%s.html' % p['id'], tags=p.get('etiquetas', [])))
        open(s.out / 'config.js', 'w', encoding='utf-8').write('window.MENU=%s;window.SITE=%s;' % (json.dumps(menu, ensure_ascii=False), json.dumps(dict(wa=K['whatsapp'], free=S['frete_gratis_acima'], nome=M['nome'], slug=slugify(M['nome']), moeda=s.moeda, pag=C['pagamentos']), ensure_ascii=False)))
        open(s.out / 'quiz-data.js', 'w', encoding='utf-8').write('window.QUIZ=%s;' % json.dumps(C['quiz'], ensure_ascii=False))
        if s.cookies_on():
            js = (MOD / 'cookies.js').read_text(encoding='utf-8').replace('__GA__', S.get('analytics_id', '')).replace('__PX__', S.get('pixel_id', ''))
            open(s.out / 'cookies.js', 'w', encoding='utf-8').write(js)
        vj = {'headers': [
            {'source': '/(.*)', 'headers': [{'key': 'X-Content-Type-Options', 'value': 'nosniff'}, {'key': 'Referrer-Policy', 'value': 'strict-origin-when-cross-origin'}, {'key': 'X-Frame-Options', 'value': 'SAMEORIGIN'}]},
            {'source': '/(.*)\\.(css|js|jpg|png|ico)', 'headers': [{'key': 'Cache-Control', 'value': 'public, max-age=86400'}]}]}
        open(s.out / 'vercel.json', 'w').write(json.dumps(vj, indent=1))
        dom = S.get('dominio', '').rstrip('/')
        pags = [f.name for f in s.out.glob('*.html') if f.name != '404.html']
        if dom:
            sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join('<url><loc>%s/%s</loc></url>\n' % (dom, 'index.html' if p == 'index.html' else p) for p in sorted(pags)) + '</urlset>\n'
            open(s.out / 'sitemap.xml', 'w').write(sm)
            open(s.out / 'robots.txt', 'w').write('User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n' % dom)
        else:
            open(s.out / 'robots.txt', 'w').write('User-agent: *\nAllow: /\n')

    # ---------- verificação ----------
    def flat(s, d, pre=''):
        r = {}
        if isinstance(d, dict):
            for k, v in d.items(): r.update(s.flat(v, pre + '.' + k if pre else k))
        elif isinstance(d, list):
            for i, v in enumerate(d): r.update(s.flat(v, '%s[%d]' % (pre, i)))
        elif isinstance(d, str): r[pre] = d
        return r
    def verificar(s):
        A = s.avisos; C = s.C
        if s.nome != DEMO_NAME:
            dem = s.flat(s.demo); cli = s.flat(C)
            skip = ('marca.cor', 'marca.fonte', 'site.idioma', 'site.moeda')
            iguais = {}
            for k, v in cli.items():
                if k in dem and dem[k] == v and len(v) > 3 and not k.startswith(skip) and not k.endswith(('.id', '.slug')) and not k.startswith(('quiz.',)):
                    iguais.setdefault(k.split('.')[0].split('[')[0], []).append(k)
            for sec, ks in iguais.items():
                A.append(('Texto de exemplo', 'Seção "%s": %d campo(s) ainda iguais ao modelo (ex.: %s)' % (sec, len(ks), ks[0])))
            if 'quiz' not in raw_keys(s.raw) and s.on.get('quiz'): A.append(('Quiz', 'O quiz ainda usa as perguntas e burgers do modelo. Troque em "quiz" ou desligue em paginas_ativas.'))
        if not re.fullmatch(r'55\d{10,11}', str(s.K.get('whatsapp', ''))): A.append(('WhatsApp', 'Número inválido. Use só dígitos com 55 + DDD + número, ex.: 5511987654321.'))
        elif s.K['whatsapp'] == '5511999990000': A.append(('WhatsApp', 'Ainda é o número fictício do modelo.'))
        if not s.S.get('dominio'): A.append(('SEO', 'Sem "dominio": sitemap, link canônico e imagem de compartilhamento ficam desligados.'))
        elif not s.S['dominio'].startswith('https://'): A.append(('SEO', '"dominio" deve começar com https://'))
        if (s.S.get('analytics_id') or s.S.get('pixel_id')) and not s.S.get('aviso_cookies'): A.append(('LGPD', 'Há medição configurada: o aviso de cookies foi ligado automaticamente.'))
        ids = [p['id'] for p in s.pratos]
        if len(ids) != len(set(ids)): A.append(('Cardápio', 'Há pratos com id repetido.'))
        for p in s.pratos:
            if not p.get('preco') or p['preco'] <= 0: A.append(('Cardápio', 'Prato sem preço: %s' % p['nome']))
            if p['categoria'] not in s.cats: A.append(('Cardápio', 'Prato "%s" usa a categoria inexistente "%s"' % (p['nome'], p['categoria'])))
            for q in p.get('combina', []):
                if q not in s.byid: A.append(('Cardápio', 'Prato "%s": "combina" aponta para id inexistente "%s"' % (p['nome'], q)))
            if not p.get('contem') and p.get('perfil'): A.append(('Alérgenos', 'Prato "%s" sem lista de alérgenos. Confirme com o cliente.' % p['nome']))
        for pid in C['mais_vendidos']:
            if pid not in s.byid: A.append(('Home', 'mais_vendidos tem id inexistente: %s' % pid))
        if s.on.get('quiz'):
            for pg in C['quiz']['perguntas']:
                for o in pg['o']:
                    for k in o[2]:
                        if k not in s.byid: A.append(('Quiz', 'Quiz aponta para prato inexistente: %s' % k))
            for k, v in C['quiz']['resultados'].items():
                if k not in s.byid or v.get('combina') not in s.byid: A.append(('Quiz', 'Resultado do quiz inválido: %s' % k))
        if not C['depoimentos'].get('itens'): A.append(('Home', 'Sem depoimentos: a seção foi omitida (use só depoimentos reais).'))
        else: A.append(('Depoimentos', 'Confirme que os depoimentos são de clientes reais e autorizados.'))
    def relatorio(s):
        print('\n=== %s ===' % s.nome)
        print('Gerado em: %s  (%d páginas, %d fotos)' % (s.out, len(list(s.out.glob('*.html'))), len(s.fotos)))
        if not s.avisos: print('Nenhuma pendência.'); return
        print('Pendências (%d):' % len(s.avisos))
        for t, m in s.avisos: print('  [%s] %s' % (t, m))

    def rodar(s):
        P = {}
        P['index.html'] = s.pg_home()
        for fn in (s.pg_cardapio, s.pg_pratos, s.pg_historia, s.pg_contato, s.pg_politica, s.pg_404):
            P.update(fn())
        if s.on.get('unidades'): P.update(s.pg_unidades())
        if s.on.get('eventos'): P.update(s.pg_eventos())
        if s.on.get('blog'): P.update(s.pg_blog())
        if s.on.get('como_fazemos'): P.update(s.pg_como())
        if s.on.get('quiz'): P.update(s.pg_quiz())
        for fn, c in P.items(): open(s.out / fn, 'w', encoding='utf-8').write(c)
        s.escrever_apoio(); s.copiar_fotos(); s.verificar(); s.relatorio()

def raw_keys(d): return set(d.keys()) if isinstance(d, dict) else set()

if __name__ == '__main__': main()
