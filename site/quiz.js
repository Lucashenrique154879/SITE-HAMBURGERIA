(function(){
'use strict';
var D=window.QUIZ||{perguntas:[],resultados:{}};var Q=D.perguntas.map(function(p){return {q:p.q,o:p.o}});
var R=D.resultados;
var ORDER=Object.keys(R);
var root=document.getElementById('quiz'),i=-1,ans=[];
var brl=function(v){return ((window.SITE&&SITE.moeda)||'R$')+' '+v.toFixed(2).replace('.',',')};
var M={};(window.MENU||[]).forEach(function(m){M[m.id]=m});
function start(){root.innerHTML='<p class="cb-red">Quiz</p><h2>Descubra o que combina com você</h2><p class="cb-muted" style="margin-top:.8rem;line-height:1.6">São cinco perguntas rápidas. Não existe resposta certa.</p><div class="cb-qnav"><span></span><button type="button" class="btn btn-primary" id="qs">Começar</button></div>';document.getElementById('qs').onclick=function(){i=0;ans=[];step()}}
function step(){
  var q=Q[i],sel=ans[i];
  root.innerHTML='<div style="display:flex;justify-content:space-between;font-size:.8rem;font-weight:700"><span class="cb-red">Pergunta '+(i+1)+' de '+Q.length+'</span></div><div class="cb-prog"><i style="width:'+((i+1)/Q.length*100)+'%"></i></div><h2></h2><div class="cb-opts"></div><div class="cb-qnav"><button type="button" class="btn btn-outline-dark cb-btn-sm" id="qb">Voltar</button><button type="button" class="btn btn-primary" id="qn" disabled>'+(i===Q.length-1?'Ver meu burger':'Próxima')+'</button></div>';
  root.querySelector('h2').textContent=q.q;
  var box=root.querySelector('.cb-opts');
  q.o.forEach(function(o,k){var b=document.createElement('button');b.type='button';b.className='cb-opt';b.setAttribute('aria-pressed',String(sel===k));b.innerHTML='<b></b><span></span>';b.firstChild.textContent=o[0];b.lastChild.textContent=o[1];
    b.onclick=function(){ans[i]=k;$$('.cb-opt').forEach(function(x,j){x.setAttribute('aria-pressed',String(j===k))});document.getElementById('qn').disabled=false};box.appendChild(b)});
  if(sel!=null)document.getElementById('qn').disabled=false;
  document.getElementById('qb').onclick=function(){if(i===0){i=-1;start()}else{i--;step()}};
  document.getElementById('qn').onclick=function(){if(i===Q.length-1)result();else{i++;step()}};
}
function $$(s){return Array.prototype.slice.call(root.querySelectorAll(s))}
function result(){
  var sc={};ORDER.forEach(function(k){sc[k]=0});
  ans.forEach(function(k,qi){var p=Q[qi].o[k][2];for(var x in p)sc[x]=(sc[x]||0)+p[x]});
  var best=ORDER.reduce(function(a,b){return sc[b]>sc[a]?b:a});
  var r=R[best],m=M[best],c=M[r.combina];
  root.innerHTML='<div class="cb-res"><p class="cb-red">Seu resultado</p><img alt=""><h2></h2><p style="line-height:1.7"></p><div class="cb-pills"></div><div class="cb-actions" style="margin-top:0"><button type="button" class="btn btn-primary" data-add="'+m.id+'">Adicionar '+m.name+' · '+brl(m.price)+'</button><a class="btn btn-outline-dark" href="'+m.url+'">Ver o prato</a></div>'+(c?'<p class="cb-muted" style="font-size:.9rem">Combina com <b>'+c.name+'</b> ('+brl(c.price)+'). <button type="button" data-add="'+c.id+'" style="text-decoration:underline;cursor:pointer;background:none;border:0;color:inherit;font:inherit;font-weight:700">Adicionar também</button></p>':'')+'<button type="button" class="cb-muted" id="qr" style="background:none;border:0;cursor:pointer;text-decoration:underline;justify-self:start">Refazer o quiz</button></div>';
  root.querySelector('img').src=m.img;root.querySelector('img').alt=m.name;
  root.querySelector('h2').textContent=r.titulo;root.querySelector('.cb-res>p:nth-of-type(2)').textContent=r.texto;
  (m.tags||[]).forEach(function(t){var s=document.createElement('span');s.className='cb-pill';s.textContent=t;root.querySelector('.cb-pills').appendChild(s)});
  document.getElementById('qr').onclick=function(){i=-1;start()};
  root.scrollIntoView({behavior:'smooth',block:'start'});
}
start();
})();
