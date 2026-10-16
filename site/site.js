(function(){
'use strict';
var SITE=window.SITE||{wa:'',free:0,nome:'',slug:'site',moeda:'R$',pag:['Pix']};var WA=SITE.wa;
var $=function(s,r){return (r||document).querySelector(s)},$$=function(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s))};
var MENU=window.MENU||[],byId={},byName={};
MENU.forEach(function(m){byId[m.id]=m;byName[m.name]=m});
var brl=function(v){return SITE.moeda+' '+v.toFixed(2).replace('.',',')};
var FREE=SITE.free;
/* estado do carrinho */
var cart={};
try{cart=JSON.parse(localStorage.getItem('cart_'+SITE.slug)||'{}')||{}}catch(e){cart={}}
Object.keys(cart).forEach(function(k){if(!byId[k]||!(cart[k]>0))delete cart[k]});
function save(){try{localStorage.setItem('cart_'+SITE.slug,JSON.stringify(cart))}catch(e){}}
function count(){return Object.keys(cart).reduce(function(a,k){return a+cart[k]},0)}
function total(){return Object.keys(cart).reduce(function(a,k){return a+cart[k]*byId[k].price},0)}
/* toast */
var tt;function toast(msg){var t=$('.cb-toast');if(t)t.remove();t=document.createElement('div');t.className='cb-toast';t.setAttribute('role','status');t.textContent=msg;document.body.appendChild(t);clearTimeout(tt);tt=setTimeout(function(){t.remove()},2000)}
/* gaveta do carrinho */
var over=document.createElement('div');over.className='cb-over';
var drawer=document.createElement('aside');drawer.className='cb-cart';drawer.setAttribute('aria-label','Seu pedido');drawer.setAttribute('aria-hidden','true');
drawer.innerHTML='<header><h2>Seu pedido</h2><button type="button" class="cb-x" aria-label="Fechar carrinho" style="font-size:1.6rem;line-height:1;cursor:pointer;background:none;border:0;color:inherit">&times;</button></header><div class="list" id="cb-list"></div><footer id="cb-foot"></footer>';
document.body.appendChild(over);document.body.appendChild(drawer);
var lastFocus;
function openCart(){lastFocus=document.activeElement;render();over.classList.add('open');drawer.classList.add('open');drawer.setAttribute('aria-hidden','false');$('.cb-x',drawer).focus()}
function closeCart(){over.classList.remove('open');drawer.classList.remove('open');drawer.setAttribute('aria-hidden','true');if(lastFocus&&lastFocus.focus)lastFocus.focus()}
over.addEventListener('click',closeCart);$('.cb-x',drawer).addEventListener('click',closeCart);
document.addEventListener('keydown',function(e){if(e.key==='Escape'){closeCart();closeFind()}});
var form={tipo:'Retirada',nome:'',end:'',pag:SITE.pag[0],obs:''};
function waText(){
  var L=['*Pedido '+SITE.nome+'*',''];
  Object.keys(cart).forEach(function(k){var m=byId[k];L.push(cart[k]+'x '+m.name+' — '+brl(cart[k]*m.price))});
  L.push('','Subtotal: '+brl(total()));
  L.push('Entrega: '+(form.tipo==='Entrega'?(FREE>0&&total()>=FREE?'grátis':'a combinar'):'retirada no balcão'));
  L.push('','Nome: '+form.nome);
  if(form.tipo==='Entrega')L.push('Endereço: '+form.end);
  L.push('Pagamento: '+form.pag);
  if(form.obs)L.push('Obs.: '+form.obs);
  return L.join('\n');
}
function render(){
  var n=count(),list=$('#cb-list'),foot=$('#cb-foot');
  var cb=$('button[aria-label^="Carrinho"]'),bd=cb&&cb.querySelector('span');
  if(cb){cb.setAttribute('aria-label','Carrinho, '+n+(n===1?' item':' itens'));if(bd)bd.textContent=n}
  if(!n){list.innerHTML='<p class="cb-muted" style="padding:2rem 0;text-align:center">Seu carrinho está vazio.<br>Escolha algo no cardápio.</p><p style="text-align:center"><a class="btn btn-primary" href="cardapio.html">Ver cardápio</a></p>';foot.innerHTML='';return}
  list.innerHTML=Object.keys(cart).map(function(k){var m=byId[k];return '<div class="cb-line"><img src="'+m.img+'" alt=""><div><b>'+m.name+'</b><div class="cb-qty"><button type="button" data-d="-1" data-id="'+k+'" aria-label="Diminuir">−</button><span>'+cart[k]+'</span><button type="button" data-d="1" data-id="'+k+'" aria-label="Aumentar">+</button></div></div><b class="cb-price" style="font-size:.9rem">'+brl(cart[k]*m.price)+'</b></div>'}).join('');
  var t=total(),pct=Math.min(100,t/FREE*100);
  var msg=t>=FREE?'Você ganhou frete grátis!':'Faltam '+brl(FREE-t)+' para frete grátis';
  var bar=FREE>0?'<div><div class="cb-bar"><i style="width:'+pct+'%"></i></div><p class="cb-muted" style="font-size:.78rem;margin-top:.3rem">'+msg+'</p></div>':'';
  foot.innerHTML=bar+
   '<div class="cb-seg"><label><input type="radio" name="cb-tipo" value="Retirada"'+(form.tipo==='Retirada'?' checked':'')+'> Retirada</label><label><input type="radio" name="cb-tipo" value="Entrega"'+(form.tipo==='Entrega'?' checked':'')+'> Entrega</label></div>'+
   '<input id="cb-nome" placeholder="Seu nome" autocomplete="name" value="'+esc(form.nome)+'">'+
   (form.tipo==='Entrega'?'<input id="cb-end" placeholder="Endereço de entrega" autocomplete="street-address" value="'+esc(form.end)+'">':'')+
   '<select id="cb-pag" aria-label="Pagamento">'+SITE.pag.map(function(o){return '<option'+(o===form.pag?' selected':'')+'>'+o+'</option>'}).join('')+'</select>'+
   '<textarea id="cb-obs" placeholder="Observações (ex.: sem cebola)" style="min-height:3.5rem">'+esc(form.obs)+'</textarea>'+
   '<div class="cb-tot"><span>Subtotal</span><span>'+brl(t)+'</span></div>'+
   '<a id="cb-send" class="btn btn-primary" target="_blank" rel="noopener" href="#">Enviar pedido pelo WhatsApp</a>'+
   '<button type="button" id="cb-clear" class="cb-muted" style="font-size:.8rem;background:none;border:0;cursor:pointer;text-decoration:underline">Limpar carrinho</button>';
  link();
}
function esc(s){return String(s).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;')}
function link(){var a=$('#cb-send');if(a)a.href='https://wa.me/'+WA+'?text='+encodeURIComponent(waText())}
drawer.addEventListener('click',function(e){
  var b=e.target.closest('[data-id]');
  if(b){var k=b.dataset.id;cart[k]=(cart[k]||0)+Number(b.dataset.d);if(cart[k]<=0)delete cart[k];save();render();return}
  if(e.target.id==='cb-clear'){cart={};save();render();return}
  if(e.target.id==='cb-send'){
    if(!form.nome.trim()||(form.tipo==='Entrega'&&!form.end.trim())){e.preventDefault();toast(!form.nome.trim()?'Informe seu nome':'Informe o endereço de entrega');var f=$(!form.nome.trim()?'#cb-nome':'#cb-end');if(f)f.focus()}
  }
});
drawer.addEventListener('input',function(e){
  var i=e.target;
  if(i.id==='cb-nome')form.nome=i.value;else if(i.id==='cb-end')form.end=i.value;else if(i.id==='cb-pag')form.pag=i.value;else if(i.id==='cb-obs')form.obs=i.value;
  else if(i.name==='cb-tipo'){form.tipo=i.value;render();return}
  link();
});
function add(id,qty){cart[id]=(cart[id]||0)+(qty||1);save();render();var cb=$('button[aria-label^="Carrinho"] span');if(cb)cb.animate([{transform:'scale(1.6)'},{transform:'scale(1)'}],{duration:260});toast(byId[id].name+' adicionado')}
document.addEventListener('click',function(e){
  var b=e.target.closest('[data-add]');if(b){add(b.dataset.add);return}
  var c=e.target.closest('button[aria-label^="Carrinho"]');if(c){openCart();return}
  var a=e.target.closest('button[aria-label^="Adicionar"]');
  if(a){var nm=a.getAttribute('aria-label').replace('Adicionar ','').replace(' ao carrinho','');if(byName[nm])add(byName[nm].id)}
});
/* busca */
var find=document.createElement('div');find.className='cb-find';
find.innerHTML='<div><input id="cb-q" type="search" placeholder="Buscar no cardápio" aria-label="Buscar no cardápio"><div id="cb-res" style="margin-top:.6rem"></div></div>';
document.body.appendChild(find);
function closeFind(){find.classList.remove('open')}
find.addEventListener('click',function(e){if(e.target===find||e.target.closest('a'))closeFind()});
function results(q){q=q.trim().toLowerCase();var r=MENU.filter(function(m){return !q||(m.name+' '+m.desc+' '+m.catName).toLowerCase().indexOf(q)>-1});
  $('#cb-res').innerHTML=r.length?r.map(function(m){return '<a href="'+m.url+'"><span>'+m.name+'</span><span>'+brl(m.price)+'</span></a>'}).join(''):'<p class="cb-muted" style="padding:1rem">Nada encontrado.</p>'}
$('#cb-q').addEventListener('input',function(e){results(e.target.value)});
var sb=$('button[aria-label="Buscar"]');if(sb)sb.addEventListener('click',function(){find.classList.add('open');results('');$('#cb-q').focus()});
var ac=$('button[aria-label="Minha conta"]');if(ac)ac.addEventListener('click',function(){toast('Área do cliente em breve')});
/* aviso do topo */
var close=$('button[aria-label="Fechar aviso"]');if(close)close.addEventListener('click',function(){close.parentElement.hidden=true});
/* menu mobile */
var menuBtn=$('button[aria-label="Abrir menu"]'),nav=$('nav[aria-label="Principal"]');
if(menuBtn&&nav){
  var panel=document.createElement('div');panel.hidden=true;panel.className='lg:hidden bg-ink text-ink-foreground';
  panel.innerHTML='<div class="mx-auto flex max-w-7xl flex-col px-4 pb-4 sm:px-6">'+$$('a',nav).map(function(a){return '<a href="'+a.getAttribute('href')+'" class="py-2.5 text-base hover:text-primary">'+a.textContent+'</a>'}).join('')+'</div>';
  $('header').appendChild(panel);
  menuBtn.addEventListener('click',function(){panel.hidden=!panel.hidden;menuBtn.setAttribute('aria-expanded',String(!panel.hidden))});
}
/* animação de entrada */
var rv=$$('.reveal');
if('IntersectionObserver' in window){var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('is-visible');io.unobserve(e.target)}})},{threshold:.08});rv.forEach(function(el){io.observe(el)})}else rv.forEach(function(el){el.classList.add('is-visible')});
/* carrosséis */
$$('section').forEach(function(sec){var car=$('.snap-mandatory',sec),pb=$('button[aria-label="Anterior"]',sec),nb=$('button[aria-label="Próximo"]',sec);
  if(!car||!pb||!nb)return;var step=function(d){car.scrollBy({left:d*(car.firstElementChild.offsetWidth+20),behavior:'smooth'})};
  pb.addEventListener('click',function(){step(-1)});nb.addEventListener('click',function(){step(1)})});
/* newsletter */
var nl=$('#nl-email');
if(nl)nl.closest('form').addEventListener('submit',function(e){e.preventDefault();if(nl.value.indexOf('@')<1){nl.focus();toast('Digite um e-mail válido');return}nl.value='';toast('Inscrição feita!')});
/* cardápio: filtro + busca */
var chips=$$('.cb-chip[data-to]');
if(chips.length){
  var cats=$$('.cb-cat');
  chips.forEach(function(c){c.addEventListener('click',function(){var t=$(c.dataset.to);if(t)t.scrollIntoView({behavior:'smooth'});history.replaceState(null,'',c.dataset.to)})});
  var spy=function(){var cur=cats[0];cats.forEach(function(c){if(!c.hidden&&c.getBoundingClientRect().top<=160)cur=c});chips.forEach(function(c){c.classList.toggle('on',c.dataset.to==='#'+cur.id)})};
  window.addEventListener('scroll',spy,{passive:true});spy();
  var q=$('#menu-q'),tag='';
  var apply=function(){var v=q?q.value.trim().toLowerCase():'',any=false;
    $$('.cb-card[data-s]').forEach(function(c){var ok=(!v||c.dataset.s.indexOf(v)>-1)&&(!tag||c.dataset.tags.split(',').indexOf(tag)>-1);c.hidden=!ok;if(ok)any=true});
    cats.forEach(function(c){c.hidden=!$$('.cb-card:not([hidden])',c).length});var e=$('#menu-empty');if(e)e.hidden=any};
  if(q)q.addEventListener('input',apply);
  $$('.cb-tag').forEach(function(t){t.addEventListener('click',function(){var on=t.getAttribute('aria-pressed')==='true';$$('.cb-tag').forEach(function(x){x.setAttribute('aria-pressed','false')});tag=on?'':t.dataset.tag;t.setAttribute('aria-pressed',String(!on));apply()})});
}
/* abas (eventos) */
$$('[data-tab]').forEach(function(b){b.addEventListener('click',function(){$$('[data-tab]').forEach(function(x){var on=x===b;x.classList.toggle('on',on);x.setAttribute('aria-selected',String(on))});$$('[data-pane]').forEach(function(p){p.hidden=p.dataset.pane!==b.dataset.tab})})});
/* filtro do blog */
$$('[data-fil]').forEach(function(b){b.addEventListener('click',function(){$$('[data-fil]').forEach(function(x){x.classList.toggle('on',x===b)});$$('#posts .cb-card').forEach(function(c){c.hidden=b.dataset.fil!=='Todos'&&c.dataset.f!==b.dataset.fil})})});
/* formulários que montam mensagem de WhatsApp */
$$('form[data-wa]').forEach(function(f){
  f.addEventListener('submit',function(e){
    e.preventDefault();
    var L=['*'+f.dataset.wa+'*',''];
    $$('input,select,textarea',f).forEach(function(i){if(i.value.trim()){var lb=i.closest('label');L.push((lb?lb.firstChild.textContent.trim():i.name)+': '+i.value.trim())}});
    var txt=L.join('\n'),box=$('.cb-result',f.parentNode);
    box.hidden=false;
    box.innerHTML='<strong>Mensagem pronta</strong><pre></pre><div class="cb-actions" style="margin:0"><a class="btn btn-primary" target="_blank" rel="noopener" href="https://wa.me/'+WA+'?text='+encodeURIComponent(txt)+'">Abrir no WhatsApp</a><button type="button" class="btn btn-outline-dark" data-copy>Copiar mensagem</button></div>';
    $('pre',box).textContent=txt;
    $('[data-copy]',box).addEventListener('click',function(){var done=function(){toast('Mensagem copiada')};try{navigator.clipboard.writeText(txt).then(done,function(){sel()})}catch(x){sel()}function sel(){var r=document.createRange();r.selectNodeContents($('pre',box));var s=getSelection();s.removeAllRanges();s.addRange(r);toast('Selecione e copie o texto')}});
    box.scrollIntoView({behavior:'smooth',block:'nearest'});
  });
});
render();
})();
