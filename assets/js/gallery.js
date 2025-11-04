// assets/js/gallery.js
(function () {
  const JSON_URL = "assets/img/gallery/generated/photos.json";
  const CONTAINER_SEL = "#cc-masonry";
  const SENTINEL_SEL  = "#cc-sentinel";
  const TITLE_SEL     = "#galleryTitle";
  const DESC_SEL      = "#galleryDesc";
  const BATCH_SIZE    = 20;

  const LABELS = {
    wildlife:     { title: "Wildlife",    desc: "Moments from the wild." },
    landscapes:   { title: "Landscapes",  desc: "Light, weather, terrain." },
    panoramas:    { title: "Panoramas",   desc: "Wide stories in a single frame." },
    documentaries:{ title: "Documentaries", desc: "Stills and BTS from films." },
    all:          { title: "Gallery",     desc: "Curated works." }
  };

  function escapeHTML(s=""){return s.replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[m]));}

  function getGalleryKey() {
    const params = new URLSearchParams(location.search);
    return (params.get("g") || "all").toLowerCase();
  }

  async function fetchData() {
    const res = await fetch(JSON_URL, { cache: "no-store" });
    if (!res.ok) throw new Error(`HTTP ${res.status} for ${JSON_URL}`);
    return res.json();
  }

  function buildSrcset(variants){
    const sizes = Object.keys(variants||{}).map(n=>parseInt(n,10)).filter(Boolean).sort((a,b)=>a-b);
    return sizes.map(s => `${variants[String(s)].src} ${s}w`).join(", ");
  }

  function largestVariant(variants){
    const sizes = Object.keys(variants||{}).map(n=>parseInt(n,10)).filter(Boolean).sort((a,b)=>b-a);
    return sizes.length ? variants[String(sizes[0])] : null;
  }

  function createCard(photo){
    const card = document.createElement("article");
    card.className = "cc-card";

    const largest = largestVariant(photo.variants);
    const holder = document.createElement("div");
    holder.className = "cc-skeleton";
    holder.style.aspectRatio = largest ? `${largest.w} / ${largest.h}` : "3 / 2";
    card.appendChild(holder);

    const img = document.createElement("img");
    img.className = "cc-thumb";
    img.alt = (photo.title && photo.title.trim()) || photo.slug || "Photo";
    img.loading = "lazy";
    img.decoding = "async";

    const srcset = buildSrcset(photo.variants);
    if (largest) img.src = largest.src;
    if (srcset)  img.srcset = srcset;
    img.sizes = "(min-width: 1200px) 33vw, (min-width: 800px) 50vw, 100vw";

    // IMPORTANT: append image now so the browser can start loading
    card.appendChild(img);
    img.addEventListener("load", () => holder.remove(), { once: true });

    const meta = document.createElement("div");
    meta.className = "cc-meta";
    const bits = [];
    if (photo.datetime) bits.push(`<time class="muted">${escapeHTML(photo.datetime)}</time>`);
    if (photo.camera)  bits.push(`<span class="muted">${escapeHTML(photo.camera)}</span>`);
    if (photo.lens)    bits.push(`<span class="muted">${escapeHTML(photo.lens)}</span>`);

    meta.innerHTML = `
      <strong>${escapeHTML((photo.title || photo.slug || "Untitled"))}</strong>
      ${bits.length ? ` · ${bits.join(" · ")}` : ""}
      ${photo.exif ? `<div class="muted">${escapeHTML(photo.exif)}</div>` : ""}
      ${(photo.description||"").trim() ? `<div class="cc-desc">${escapeHTML(photo.description)}</div>` : ""}
    `;
    card.appendChild(meta);

    return card;
  }

  function setHeading(gKey){
    const meta = LABELS[gKey] || LABELS.all;
    const t = document.querySelector(TITLE_SEL);
    const d = document.querySelector(DESC_SEL);
    if (t) t.textContent = meta.title;
    if (d) d.textContent = meta.desc;

    // optional: highlight active nav item
    document.querySelectorAll('header nav a').forEach(a=>{
      const url = new URL(a.href, location.origin);
      const key = (new URLSearchParams(url.search).get("g") || "all").toLowerCase();
      a.classList.toggle("active", key === gKey);
    });
  }

  async function init(){
    const container = document.querySelector(CONTAINER_SEL);
    const sentinel  = document.querySelector(SENTINEL_SEL);
    if (!container) return;

    const gKey = getGalleryKey();   // e.g. "wildlife" | "landscapes" | "all"
    setHeading(gKey);

    let data = await fetchData();

    // 🔍 FILTER HERE
    if (gKey !== "all") {
      data = data.filter(p => (p.gallery || "").toLowerCase() === gKey);
    }

    // (Optional) log counts so you can sanity-check in DevTools
    console.log(`[gallery] key="${gKey}" → ${data.length} items`);

    // sort newest first
    data.sort((a,b)=>(b.datetime||"").localeCompare(a.datetime||""));

    let idx = 0;
    function appendBatch(){
      const end = Math.min(idx + BATCH_SIZE, data.length);
      const frag = document.createDocumentFragment();
      for (; idx < end; idx++) frag.appendChild(createCard(data[idx]));
      container.appendChild(frag);
    }

    appendBatch();

    if (!sentinel) return;
    const io = new IntersectionObserver((entries)=>{
      for (const entry of entries) {
        if (entry.isIntersecting) {
          if (idx < data.length) appendBatch();
          if (idx >= data.length) { io.disconnect(); sentinel.remove(); }
        }
      }
    }, { rootMargin: "800px 0px" });

    io.observe(sentinel);
  }

  document.addEventListener("DOMContentLoaded", init);
})();


(function(){
  const grid = document.getElementById('cc-masonry');
  const lgx  = document.getElementById('lgx');
  if(!grid || !lgx) return;

  const imgEl    = lgx.querySelector('.lgx__img');
  const capEl    = lgx.querySelector('.lgx__caption');
  const btnClose = lgx.querySelector('.lgx__close');
  const btnPrev  = lgx.querySelector('.lgx__prev');
  const btnNext  = lgx.querySelector('.lgx__next');
  const btnPlay  = lgx.querySelector('.lgx__play');
  const btnPause = lgx.querySelector('.lgx__pause');

  let nodes = [];       // <img.cc-thumb> nodes
  let idx = 0;
  let playing = false;
  let timer = null;
  const DURATION = 3000;

  // Parse srcset and return the largest candidate URL (fallback to src)
  function largestSrc(img){
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
    // Prefer <strong> inside sibling .cc-meta; fallback to alt
    const card = img.closest('.cc-card');
    const strong = card?.querySelector('.cc-meta strong')?.textContent?.trim();
    const extra  = card?.querySelector('.cc-meta .muted')?.textContent?.trim();
    const alt    = img.getAttribute('alt') || '';
    return strong ? (extra ? `${strong} · ${extra}` : strong) : alt;
  }

  function collect(){
    nodes = Array.from(grid.querySelectorAll('img.cc-thumb'));
  }
  collect();

  // Re-collect when JSON adds new cards
  new MutationObserver(collect).observe(grid, {childList:true, subtree:true});

  function show(i){
    if(!nodes.length) return;
    idx = (i + nodes.length) % nodes.length;
    const img = nodes[idx];
    imgEl.src = largestSrc(img);
    imgEl.alt = img.alt || '';
    capEl.textContent = captionFor(img);

    // Preload neighbors
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
  function stop(){
    playing = false;
    btnPlay.style.display = '';
    btnPause.style.display = 'none';
    if(timer){ clearInterval(timer); timer = null; }
  }
  function togglePlay(){ playing ? stop() : play(); }

  // Delegate clicks (works for dynamically added items)
  grid.addEventListener('click', e=>{
    const img = e.target.closest('img.cc-thumb');
    if(!img) return;
    e.preventDefault();
    collect();
    const i = nodes.indexOf(img);
    open(i >= 0 ? i : 0);
  });

  // Buttons
  btnClose.addEventListener('click', close);
  btnNext .addEventListener('click', next);
  btnPrev .addEventListener('click', prev);
  btnPlay .addEventListener('click', play);
  btnPause.addEventListener('click', stop);

  // Keyboard
  document.addEventListener('keydown', e=>{
    if(!lgx.classList.contains('show')) return;
    if(e.key === 'Escape') close();
    else if(e.key === 'ArrowRight') next();
    else if(e.key === 'ArrowLeft')  prev();
    else if(e.key === ' '){ e.preventDefault(); togglePlay(); }
  });

  // Swipe
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

  // Close when clicking backdrop (not image/buttons)
  lgx.addEventListener('click', e=>{
    const isImg = e.target === imgEl;
    const isBtn = e.target.closest && e.target.closest('.lgx__btn');
    if(!isImg && !isBtn) close();
  });
})();
