let currentSlide = 0;
let hideCursorTimer = null;
function slides(){ return [...document.querySelectorAll('.slide')]; }
function goToSlide(index, updateHash=true){
  const all=slides(); currentSlide=Math.max(0,Math.min(index,all.length-1));
  all.forEach((s,i)=>s.classList.toggle('active', i===currentSlide));
  document.querySelector('.counter').textContent = `${String(currentSlide+1).padStart(2,'0')} / ${String(all.length).padStart(2,'0')}`;
  document.querySelector('.progress span').style.width = `${((currentSlide+1)/all.length)*100}%`;
  if(updateHash) history.replaceState(null,'',`#slide-${currentSlide+1}`);
  animateActiveSlide();
}
function nextSlide(){ goToSlide(currentSlide+1); }
function prevSlide(){ goToSlide(currentSlide-1); }
function animateActiveSlide(){
  document.querySelectorAll('.slide.active .counter-number').forEach(el=>animateNumber(el));
  const slide=slides()[currentSlide];
  if(slide?.dataset.render){ renderSlideCharts(slide); }
}
function buildMenu(){
  const list=document.querySelector('.menu-list'); list.innerHTML='';
  slides().forEach((s,i)=>{ const btn=document.createElement('button'); btn.textContent=`${String(i+1).padStart(2,'0')} — ${s.dataset.title || s.querySelector('h2,h1')?.textContent || 'Slide'}`; btn.onclick=()=>{ goToSlide(i); closeMenu(); }; list.appendChild(btn); });
}
function openMenu(){ document.querySelector('.side-menu').classList.add('open'); }
function closeMenu(){ document.querySelector('.side-menu').classList.remove('open'); }
function toggleFullscreen(){ if(!document.fullscreenElement) document.documentElement.requestFullscreen?.(); else document.exitFullscreen?.(); }
function presentationMode(){ toggleFullscreen(); document.body.classList.add('presenting'); }
function showCursor(){ document.body.classList.remove('presenting'); clearTimeout(hideCursorTimer); hideCursorTimer=setTimeout(()=>{ if(document.fullscreenElement) document.body.classList.add('presenting'); },2200); }
function initNavigation(){
  document.querySelector('[data-next]').onclick=nextSlide; document.querySelector('[data-prev]').onclick=prevSlide; document.querySelector('[data-menu]').onclick=openMenu; document.querySelector('[data-close-menu]').onclick=closeMenu; document.querySelector('[data-fullscreen]').onclick=presentationMode; document.querySelector('[data-source]').onclick=()=>document.querySelector('.modal-backdrop').classList.add('open'); document.querySelector('[data-close-modal]').onclick=()=>document.querySelector('.modal-backdrop').classList.remove('open');
  document.addEventListener('keydown', e=>{ if(e.key==='ArrowRight'||e.key==='PageDown'||e.key===' ') { e.preventDefault(); nextSlide(); } if(e.key==='ArrowLeft'||e.key==='PageUp') prevSlide(); if(e.key==='Home') goToSlide(0); if(e.key==='End') goToSlide(slides().length-1); if(e.key==='Escape'){ closeMenu(); document.querySelector('.modal-backdrop').classList.remove('open'); } });
  document.addEventListener('mousemove', showCursor);
  buildMenu(); const match=location.hash.match(/slide-(\d+)/); goToSlide(match?Number(match[1])-1:0,false);
}
