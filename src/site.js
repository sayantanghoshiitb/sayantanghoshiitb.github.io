const nav=document.querySelector('.navigation'),toggle=document.querySelector('.menu-toggle');
toggle?.addEventListener('click',()=>{const open=nav.classList.toggle('open');toggle.setAttribute('aria-expanded',String(open));});
document.querySelectorAll('.nav-menu button').forEach(b=>b.addEventListener('click',()=>{const open=b.parentElement.classList.toggle('expanded');b.setAttribute('aria-expanded',String(open));}));
document.addEventListener('keydown',e=>{if(e.key==='Escape'){nav?.classList.remove('open');toggle?.setAttribute('aria-expanded','false');}});
document.addEventListener('click',e=>{if(!nav?.contains(e.target)){nav?.classList.remove('open');toggle?.setAttribute('aria-expanded','false');}});
const gallery=document.querySelector('.home-gallery');
function layout(){if(!gallery)return;const items=[...gallery.children],w=gallery.clientWidth;let cols=innerWidth<=480?1:innerWidth<=767?3:innerWidth<=1400?4:5;const gap=5,cw=(w-gap*(cols-1))/cols,heights=Array(cols).fill(0);items.forEach(item=>{const img=item.querySelector('img'),col=heights.indexOf(Math.min(...heights));item.style.width=cw+'px';item.style.left=col*(cw+gap)+'px';item.style.top=heights[col]+'px';const ratio=Number(img.height)/Number(img.width);heights[col]+=cw*(Number(img.getAttribute('height'))/Number(img.getAttribute('width'))||ratio||1)+gap;});gallery.style.height=Math.max(...heights)+'px';}
layout();if(gallery)new ResizeObserver(layout).observe(gallery);
const dialog=document.querySelector('.lightbox'),photo=dialog?.querySelector('img'),caption=dialog?.querySelector('.lightbox-caption');let active=0,opener;const links=[...document.querySelectorAll('a[data-lightbox]')];
function showPhoto(i){active=(i+links.length)%links.length;const a=links[active];photo.src=a.href;photo.alt=a.querySelector('img')?.alt||'Photograph by Sayantan Ghosh';caption.textContent=`${active+1} / ${links.length}`;}
links.forEach((a,i)=>a.addEventListener('click',e=>{e.preventDefault();opener=a;showPhoto(i);dialog.showModal();}));
dialog?.querySelector('[data-close]').addEventListener('click',()=>dialog.close());dialog?.querySelector('[data-prev]').addEventListener('click',()=>showPhoto(active-1));dialog?.querySelector('[data-next]').addEventListener('click',()=>showPhoto(active+1));dialog?.addEventListener('close',()=>opener?.focus());dialog?.addEventListener('click',e=>{if(e.target===dialog)dialog.close();});dialog?.addEventListener('keydown',e=>{if(e.key==='ArrowLeft')showPhoto(active-1);if(e.key==='ArrowRight')showPhoto(active+1);});

const siteLoader=document.querySelector('#home-loader');
if(siteLoader&&document.documentElement.classList.contains('page-loading')){
 const started=performance.now();
 const isPortfolio=!!document.querySelector('.home-gallery');
 const images=isPortfolio?[...document.querySelectorAll('.home-gallery img')]:[...document.querySelectorAll('img')].filter(img=>(img.currentSrc||img.getAttribute('src'))&&!img.dataset.src&&(img.loading!=='lazy'||img.getBoundingClientRect().top<innerHeight));
 Promise.all(images.map(img=>img.decode().catch(()=>undefined))).then(()=>{
  const remaining=Math.max(0,650-(performance.now()-started));
  setTimeout(()=>{
   siteLoader.classList.add('is-done');
   document.documentElement.classList.remove('page-loading');
   try{sessionStorage.setItem('sayantan-loader-seen','1')}catch(e){}
   setTimeout(()=>siteLoader.remove(),450);
  },remaining);
 });
}
