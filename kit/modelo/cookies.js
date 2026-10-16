(function(){
var GA='__GA__',PX='__PX__',K='cookies_ok';
function get(){try{return localStorage.getItem(K)}catch(e){return null}}
function set(v){try{localStorage.setItem(K,v)}catch(e){}}
function load(){
  if(GA){var s=document.createElement('script');s.async=true;s.src='https://www.googletagmanager.com/gtag/js?id='+GA;document.head.appendChild(s);window.dataLayer=window.dataLayer||[];window.gtag=function(){dataLayer.push(arguments)};gtag('js',new Date());gtag('config',GA)}
  if(PX){!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');fbq('init',PX);fbq('track','PageView')}
}
var v=get();
if(v==='1'){load();return}
if(v==='0')return;
var b=document.createElement('div');b.className='cb-cookie';b.setAttribute('role','dialog');b.setAttribute('aria-label','Aviso de cookies');
b.innerHTML='<p>Usamos cookies para medir visitas e melhorar o site. Veja a <a href="politica.html">política de privacidade</a>.</p><div><button type="button" class="btn btn-outline-dark cb-btn-sm" data-n>Recusar</button><button type="button" class="btn btn-primary cb-btn-sm" data-y>Aceitar</button></div>';
document.body.appendChild(b);
b.querySelector('[data-y]').onclick=function(){set('1');b.remove();load()};
b.querySelector('[data-n]').onclick=function(){set('0');b.remove()};
})();
