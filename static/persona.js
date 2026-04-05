// persona.js — RA · DZI · MA visual persona rail + mode sync

document.addEventListener("DOMContentLoaded", () => {
  const body   = document.body;
  const avatar = document.getElementById("personaAvatar");

  const raBtn  = document.getElementById("personaRaBtn");
  const dziBtn = document.getElementById("personaDziBtn");
  const maBtn  = document.getElementById("personaMaBtn");

  // Top mode buttons: Outer Court, Inner Court, Holy of Holies
  const modeButtons = document.querySelectorAll(".mode-btn");

  let currentPersona = "RA"; // default

  function setPersona(mode) {
    currentPersona = mode;

    // body colour mode
    body.classList.remove("mode-ra", "mode-dzi", "mode-ma");
    if (mode === "RA")  body.classList.add("mode-ra");
    if (mode === "DZI") body.classList.add("mode-dzi");
    if (mode === "MA")  body.classList.add("mode-ma");

    // highlight rail buttons
    [raBtn, dziBtn, maBtn].forEach((btn) => {
      if (!btn) return;
      btn.classList.remove("active");
    });

    if (mode === "RA" && raBtn)  raBtn.classList.add("active");
    if (mode === "DZI" && dziBtn) dziBtn.classList.add("active");
    if (mode === "MA" && maBtn)  maBtn.classList.add("active");

    // swap avatar
    if (avatar) {
      if (mode === "RA"  && avatar.dataset.ra)   avatar.src = avatar.dataset.ra;
      if (mode === "DZI" && avatar.dataset.dzi) avatar.src = avatar.dataset.dzi;
      if (mode === "MA"  && avatar.dataset.ma)   avatar.src = avatar.dataset.ma;
    }
  }

  // Hook up RA · DZI · MA rail
  if (raBtn)  raBtn.addEventListener("click", () => setPersona("RA"));
  if (dziBtn) dziBtn.addEventListener("click", () => setPersona("DZI"));
  if (maBtn)  maBtn.addEventListener("click", () => setPersona("MA"));

  // Hook up Outer / Inner / Holy to same personas
  if (modeButtons.length >= 3) {
    // Outer Court  → RA
    modeButtons[0].addEventListener("click", () => setPersona("RA"));
    // Inner Court  → DZI
    modeButtons[1].addEventListener("click", () => setPersona("DZI"));
    // Holy of Holies → MA
    modeButtons[2].addEventListener("click", () => setPersona("MA"));
  }

  // expose to app.js
  window.getCurrentPersona = () => currentPersona;

  // initial state
  setPersona("RA");
});