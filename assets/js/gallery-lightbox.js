(function(){
  const grid = document.getElementById('cc-masonry');
  const lgx  = document.getElementById('lgx');
  if(!grid || !lgx) return;

  const filterButtons = Array.from(document.querySelectorAll('[data-filter]'));
  const countEl = document.getElementById('gallery-count');
  const imgEl    = lgx.querySelector('.lgx__img');
  const capEl    = lgx.querySelector('.lgx__caption');
  const btnClose = lgx.querySelector('.lgx__close');
  const btnPrev  = lgx.querySelector('.lgx__prev');
  const btnNext  = lgx.querySelector('.lgx__next');
  const btnPlay  = lgx.querySelector('.lgx__play');
  const btnPause = lgx.querySelector('.lgx__pause');

  let nodes = [];
  let idx = 0;
  let playing = false;
  let timer = null;
  const DURATION = 3000;

  function largestSrc(img){
    const full = img.getAttribute('data-full');
    if(full) return full;
    const ss = img.getAttribute('srcset');
    if(!ss) return img.currentSrc || img.src;
    let bestURL = img.src, bestW = 0;
    ss.split(',').forEach(part=>{
      const [url, wstr] = part.trim().split(/\s+/);
      const w = parseInt(wstr,10) || 0;
      if(w > bestW){ bestW = w; bestURL = url; }
    });
    return bestURL;
  }

  function captionFor(img){
    const card = img.closest('.cc-card');
    const strong = card?.querySelector('.cc-meta h3, .cc-meta strong')?.textContent?.trim();
    const extra  = card?.querySelector('.cc-meta .muted')?.textContent?.trim();
    const alt    = img.getAttribute('alt') || '';
    return strong ? (extra ? `${strong} · ${extra}` : strong) : alt;
  }

  function collect(){
    nodes = Array.from(grid.querySelectorAll('.cc-card:not([hidden]) img.cc-thumb'));
  }
  collect();

  function applyFilter(filter, updateHash){
    const active = filter || 'all';
    let shown = 0;
    Array.from(grid.querySelectorAll('.cc-card')).forEach(card=>{
      const tags = (card.getAttribute('data-tags') || '').split(/\s+/);
      const visible = active === 'all' || tags.includes(active);
      card.hidden = !visible;
      if(visible) shown += 1;
    });
    filterButtons.forEach(btn=>{
      btn.classList.toggle('is-active', btn.getAttribute('data-filter') === active);
    });
    if(countEl) countEl.textContent = String(shown);
    collect();
    if(updateHash && active !== 'all') history.replaceState(null, '', `#${active}`);
    if(updateHash && active === 'all') history.replaceState(null, '', location.pathname);
  }

  if(filterButtons.length){
    filterButtons.forEach(btn=>{
      btn.addEventListener('click', ()=>{
        applyFilter(btn.getAttribute('data-filter') || 'all', true);
      });
    });
    const initial = location.hash.replace('#', '');
    const valid = filterButtons.some(btn=>btn.getAttribute('data-filter') === initial);
    applyFilter(valid ? initial : 'all', false);
  }

  function show(i){
    if(!nodes.length) return;
    idx = (i + nodes.length) % nodes.length;
    const img = nodes[idx];
    imgEl.src = largestSrc(img);
    imgEl.alt = img.alt || '';
    capEl.textContent = captionFor(img);

    [-1,1].forEach(d=>{
      const j = (idx + d + nodes.length) % nodes.length;
      const nimg = nodes[j];
      const pre = new Image(); pre.src = largestSrc(nimg);
    });
  }

  function open(i){
    show(i);
    lgx.classList.add('show');
    lgx.setAttribute('aria-hidden','false');
    document.documentElement.style.overflow = 'hidden';
  }

  function stop(){
    playing = false;
    btnPlay.style.display = '';
    btnPause.style.display = 'none';
    if(timer){ clearInterval(timer); timer = null; }
  }

  function close(){
    lgx.classList.remove('show');
    lgx.setAttribute('aria-hidden','true');
    document.documentElement.style.overflow = '';
    stop();
  }
  function next(){ show(idx+1); }
  function prev(){ show(idx-1); }

  function play(){
    if(playing || !nodes.length) return;
    playing = true;
    btnPlay.style.display = 'none';
    btnPause.style.display = '';
    timer = setInterval(next, DURATION);
  }
  function togglePlay(){ playing ? stop() : play(); }

  grid.addEventListener('click', e=>{
    const img = e.target.closest('img.cc-thumb');
    if(!img) return;
    e.preventDefault();
    collect();
    const i = nodes.indexOf(img);
    open(i >= 0 ? i : 0);
  });

  btnClose.addEventListener('click', close);
  btnNext .addEventListener('click', next);
  btnPrev .addEventListener('click', prev);
  btnPlay .addEventListener('click', play);
  btnPause.addEventListener('click', stop);

  document.addEventListener('keydown', e=>{
    if(!lgx.classList.contains('show')) return;
    if(e.key === 'Escape') close();
    else if(e.key === 'ArrowRight') next();
    else if(e.key === 'ArrowLeft')  prev();
    else if(e.key === ' '){ e.preventDefault(); togglePlay(); }
  });

  let sx=0, sy=0;
  lgx.addEventListener('touchstart', e=>{
    const t = e.touches[0]; if(!t) return;
    sx = t.clientX; sy = t.clientY;
  }, {passive:true});
  lgx.addEventListener('touchend', e=>{
    const t = e.changedTouches[0]; if(!t) return;
    const dx = t.clientX - sx, dy = t.clientY - sy;
    if(Math.abs(dx) > 40 && Math.abs(dx) > Math.abs(dy)) (dx<0 ? next() : prev());
  });

  lgx.addEventListener('click', e=>{
    const isImg = e.target === imgEl;
    const isBtn = e.target.closest && e.target.closest('.lgx__btn');
    if(!isImg && !isBtn) close();
  });
})();
