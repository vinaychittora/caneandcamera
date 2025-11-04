// assets/js/documentaries.js
document.addEventListener("DOMContentLoaded", () => {
  const grid = document.getElementById("docuGrid");

  // ▶️ Add your YouTube videos here
  const videos = [
    {
      id: "hjRtHOO40L4",
      title: "Only 150 Left | Rare Great Indian Bustard Courtship Display (Radheyshyam’s Legacy)",
      desc: "Courtship displays of the Great Indian Bustard in Rajasthan’s Thar Desert."
    },
    {
      id: "4uPAnSuYyb0",
      title: "Struggles of Desert Fox Family | Wildlife Documentary | Desert national park (India) | 4K",
      desc: "Exploring the revival of Mukundara Hills Tiger Reserve and its local communities."
    },
    {
      id: "_UM3xL7yUSY",
      title: "Flamingos, Raptors, Pelicans & Hoopoe-Lark | Little Rann of Kutch, India | Wildlife in 4K",
      desc: "A short story on harriers and winter raptors of Sorsan Grasslands."
    }
  ];

  // build cards
  const frag = document.createDocumentFragment();
  videos.forEach(v => {
    const card = document.createElement("article");
    card.className = "docu-card";
    card.innerHTML = `
      <iframe
        src="https://www.youtube.com/embed/${v.id}"
        title="${v.title}"
        loading="lazy"
        allowfullscreen>
      </iframe>
      <div class="docu-meta">
        <h3>${v.title}</h3>
        <p>${v.desc}</p>
      </div>
    `;
    frag.appendChild(card);
  });
  grid.appendChild(frag);
});
