const data=JSON.parse(document.querySelector('#bird-data').textContent);
const search=document.querySelector('#bird-search'),country=document.querySelector('#bird-country'),photoOnly=document.querySelector('#bird-photo'),sort=document.querySelector('#bird-sort');
function enhanceSelect(select,label){
 const box=document.createElement('div'),trigger=document.createElement('button'),menu=document.createElement('div'),options=[...select.options];
 box.className='bird-select';trigger.type='button';trigger.className='bird-select-trigger';trigger.setAttribute('role','combobox');trigger.setAttribute('aria-haspopup','listbox');trigger.setAttribute('aria-expanded','false');trigger.setAttribute('aria-label',label);menu.className='bird-select-menu';menu.hidden=true;menu.id=select.id+'-menu';menu.setAttribute('role','listbox');menu.setAttribute('aria-label',label);
 for(const option of options){const item=document.createElement('button');item.type='button';item.className='bird-select-option';item.setAttribute('role','option');item.dataset.value=option.value;item.textContent=option.textContent;item.addEventListener('click',()=>{select.value=option.value;select.dispatchEvent(new Event('change',{bubbles:true}));select.dispatchEvent(new Event('input',{bubbles:true}));close();trigger.focus();});menu.append(item);}
 trigger.setAttribute('aria-controls',menu.id);box.append(trigger,menu);select.hidden=true;select.after(box);
 function refresh(){const active=menu.querySelector(`[data-value="${CSS.escape(select.value)}"]`);trigger.textContent=active?.textContent||options[0].textContent;menu.querySelectorAll('[role=option]').forEach(item=>item.setAttribute('aria-selected',String(item.dataset.value===select.value)));}
 function close(){menu.hidden=true;trigger.setAttribute('aria-expanded','false');}
 function open(){document.querySelectorAll('.bird-select-menu').forEach(other=>{if(other!==menu){other.hidden=true;other.previousElementSibling.setAttribute('aria-expanded','false');}});menu.hidden=false;trigger.setAttribute('aria-expanded','true');menu.querySelector('[aria-selected="true"]')?.focus();}
 trigger.addEventListener('click',()=>menu.hidden?open():close());trigger.addEventListener('keydown',e=>{if(['ArrowDown','ArrowUp','Enter',' '].includes(e.key)){e.preventDefault();open();}if(e.key==='Escape')close();});
 menu.addEventListener('keydown',e=>{const items=[...menu.querySelectorAll('[role=option]')],i=items.indexOf(document.activeElement);if(e.key==='Escape'){e.preventDefault();close();trigger.focus();}else if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();items[(i+(e.key==='ArrowDown'?1:-1)+items.length)%items.length].focus();}else if(e.key==='Home'||e.key==='End'){e.preventDefault();items[e.key==='Home'?0:items.length-1].focus();}});
 select.addEventListener('change',refresh);document.addEventListener('click',e=>{if(!box.contains(e.target))close();});refresh();return refresh;
}
const refreshCountry=enhanceSelect(country,'Country filter');enhanceSelect(sort,'Sort birds');
const cards=[...document.querySelectorAll('.bird-card')],map=document.querySelector('#bird-map');
let selectedRegion='';
const images=new IntersectionObserver(entries=>{for(const entry of entries){if(!entry.isIntersecting||entry.target.closest('[hidden]'))continue;const img=entry.target;img.src=img.dataset.src;images.unobserve(img);}}, {rootMargin:'350px'});
for(const img of document.querySelectorAll('img[data-src]'))images.observe(img);
function filter(){
 const q=search.value.toLocaleLowerCase().trim(),c=country.value;
 const ordered=[...cards].sort((a,b)=>sort.value==='recent'?b.dataset.date.localeCompare(a.dataset.date):a.dataset.name.localeCompare(b.dataset.name));
 for(const card of ordered){
  const show=(!q||card.dataset.search.includes(q))&&(!c||card.dataset.countries.split(',').includes(c))&&(!selectedRegion||card.dataset.regions.split(',').includes(selectedRegion))&&(!photoOnly.checked||card.dataset.photo==='true');
  card.hidden=!show;card.parentElement.append(card);if(show){const img=card.querySelector('img[data-src]:not([src])');if(img){images.unobserve(img);images.observe(img);}}
 }
 const photoCount=document.querySelector('#photo-count');
 if(photoCount)photoCount.textContent=`(${photoOnly.checked?cards.filter(card=>card.dataset.photo==='true').length:cards.length} species)`;
 const visible=cards.filter(card=>!card.hidden).length;
 document.querySelector('#no-results').hidden=visible>0;
 document.querySelectorAll('[data-country]').forEach(el=>el.classList.toggle('selected',el.dataset.country===c));
 document.querySelectorAll('[data-region]').forEach(el=>el.classList.toggle('selected',el.dataset.region===selectedRegion));
}
function fit(el){
 const b=el.getBBox();if(!b.width||!b.height)return;
 const padding=Math.max(b.width,b.height)*.12;map.setAttribute('viewBox',`${b.x-padding} ${b.y-padding} ${b.width+padding*2} ${b.height+padding*2}`);
}
function renderList(){
 const list=document.querySelector('#region-list');list.replaceChildren();
 const c=country.value,rows=c?(data.regions[c]||[]):data.countries.map(it=>[it.code,it.count]);
 document.querySelector('#region-heading').textContent=c?'By state / region':'By country';
 for(const [code,count] of [...rows].sort((a,b)=>b[1]-a[1])){
  const li=document.createElement('li'),button=document.createElement('button'),name=document.createElement('span'),number=document.createElement('b');
  if(c)button.dataset.region=code;else button.dataset.country=code;
  name.textContent=c?(map.querySelector(`[data-region="${code}"]`)?.dataset.name||code):data.names[code]||code;number.textContent=count;button.append(name,number);li.append(button);list.append(li);
 }
 if(!rows.length){const li=document.createElement('li');li.textContent='No regional totals available';list.append(li);}
}
function zoomCountry(code){
 country.value=code;refreshCountry();selectedRegion='';
 document.querySelectorAll('.state-layer').forEach(layer=>layer.toggleAttribute('hidden',layer.dataset.mapCountry!==code));
 document.querySelector('#world-layer').classList.toggle('zoomed',Boolean(code));
 const layer=map.querySelector(`[data-map-country="${code}"]`),path=map.querySelector(`#world-layer [data-country="${code}"]`);
 if(code&&(layer?.childElementCount||path))fit(layer?.childElementCount?layer:path);else map.setAttribute('viewBox','0 0 900 450');
 document.querySelector('#map-country').hidden=!code;document.querySelector('#map-country').textContent=data.names[code]||code;
 document.querySelector('#map-place').textContent='';document.querySelector('#map-back').hidden=!code;
 renderList();filter();
}
function zoomRegion(code){
 const path=map.querySelector(`[data-region="${code}"]`);if(!path)return;
 selectedRegion=code;fit(path);document.querySelector('#map-place').textContent=path.dataset.name;filter();
}
function activate(event){const region=event.target.closest('[data-region]'),c=event.target.closest('[data-country]');if(region)zoomRegion(region.dataset.region);else if(c)zoomCountry(c.dataset.country);}
map.addEventListener('click',activate);document.querySelector('#region-list').addEventListener('click',activate);
map.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();activate(event);}});
document.querySelector('#map-world').addEventListener('click',()=>zoomCountry(''));
document.querySelector('#map-country').addEventListener('click',()=>zoomCountry(country.value));
document.querySelector('#map-back').addEventListener('click',()=>selectedRegion?zoomCountry(country.value):zoomCountry(''));
country.addEventListener('change',()=>zoomCountry(country.value));[search,photoOnly,sort].forEach(el=>el.addEventListener('input',filter));
document.querySelector('#reset-filters').addEventListener('click',()=>{search.value='';photoOnly.checked=true;sort.value='name';sort.dispatchEvent(new Event('change',{bubbles:true}));country.value='';country.dispatchEvent(new Event('change',{bubbles:true}));});
filter();
