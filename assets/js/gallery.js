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
