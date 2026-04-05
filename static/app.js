// app.js — Throne of Anhu · RA
// Client for FastAPI backend (main.py / throne_engine.py)

const THRONE_API_ENDPOINT = "/api/throne";
const ANI_VAULT_ENDPOINT = "/api/ani/scrolls";
const SCROLL_BY_TITLE_ENDPOINT = "/api/scroll_by_title";

// ---- DOM HOOKS ----
const messagesEl = document.getElementById("messages");
const userInput = document.getElementById("userInput");
const languageSelect = document.getElementById("languageSelect");
const chatForm = document.getElementById("chatForm");
const sendBtn = document.getElementById("sendBtn");
const viewScrollsBtn = document.getElementById("viewScrollsBtn");

// CLEAR CHAT BUTTON (rail)
const clearChatBtn = document.getElementById("clearChatBtn");

// ---- HOUSE OF WISDOM (WITNESSES) ----
const witnessToggleBar = document.getElementById("witnessToggleBar");
const witnessPanel = document.getElementById("witnessPanel");
const witnessContent = document.getElementById("witnessContent");
const toggleWitnessBtn = document.getElementById("toggleWitnessBtn");
const closeWitnessBtn = document.getElementById("closeWitnessBtn");

// Hourglass + typing indicator
const hourglassEl = document.getElementById("hourglass");
const typingIndicator = document.getElementById("typingIndicator");

// Pin bar
const pinBar = document.getElementById("pinBar");
const pinnedScrollChip = document.getElementById("pinnedScrollChip");
const pinnedScrollTitleEl = document.getElementById("pinnedScrollTitle");
const clearPinBtn = document.getElementById("clearPinBtn");

// Scroll modal
const scrollModal = document.getElementById("scrollModal");
const closeScrollModalBtn = document.getElementById("closeScrollModal");
const scrollListEl = document.getElementById("scrollList");
const scrollSearchInput = document.getElementById("scrollSearchInput");
const scrollSearchBtn = document.getElementById("scrollSearchBtn");

// Scroll preview modal
const scrollPreviewModal = document.getElementById("scrollPreviewModal");
const scrollPreviewTitleEl = document.getElementById("scrollPreviewTitle");
const scrollPreviewSeriesEl = document.getElementById("scrollPreviewSeries");
const scrollPreviewBodyEl = document.getElementById("scrollPreviewBody");
const scrollPreviewCloseBtn = document.getElementById("scrollPreviewCloseBtn");
const scrollPreviewCancelBtn = document.getElementById("scrollPreviewCancelBtn");
const scrollPreviewOpenFullBtn = document.getElementById(
  "scrollPreviewOpenFullBtn"
);
let currentPreviewTitle = null;

// ANI VAULT (slide-over)
const vaultPanel = document.getElementById("vaultPanel");
const closeVaultBtn = document.getElementById("closeVaultBtn");
const vaultSearchInput = document.getElementById("vaultSearchInput");
const vaultSearchBtn = document.getElementById("vaultSearchBtn");
const vaultListEl = document.getElementById("vaultList");
const vaultDetailTitleEl = document.getElementById("vaultDetailTitle");
const vaultDetailMetaEl = document.getElementById("vaultDetailMeta");
const vaultDetailTextEl = document.getElementById("vaultDetailText");

// ---- AUTH & HISTORY DOM HOOKS ----
const loginBtn = document.getElementById("loginBtn");
const userMenu = document.getElementById("userMenu");
const userAvatar = document.getElementById("userAvatar");
const userName = document.getElementById("userName");
const historyToggleBtn = document.getElementById("historyToggleBtn");
const historySidebar = document.getElementById("historySidebar");
const closeHistoryBtn = document.getElementById("closeHistoryBtn");
const newChatBtn = document.getElementById("newChatBtn");
const historyList = document.getElementById("historyList");

// ---- PRICING MODAL DOM HOOKS ----
const upgradeBtn = document.getElementById("upgradeBtn");
const billingBtn = document.getElementById("billingBtn");
const rushangaBtn = document.getElementById("rushangaBtn");
const pricingModal = document.getElementById("pricingModal");
const closePricingBtn = document.getElementById("closePricingBtn");
const subscribeSeekerBtn = document.getElementById("subscribeSeekerBtn");

// ---- RUSHANGA ADMIN PANEL ----
const rushangaModal = document.getElementById("rushangaModal");
const closeRushangaBtn = document.getElementById("closeRushangaBtn");
const rushangaSubscribersList = document.getElementById("rushangaSubscribersList");
const rushangaSearchInput = document.getElementById("rushangaSearchInput");
const rushangaRefreshBtn = document.getElementById("rushangaRefreshBtn");
const grantAccessBtn = document.getElementById("grantAccessBtn");
const grantEmail = document.getElementById("grantEmail");
const grantDuration = document.getElementById("grantDuration");
const grantNote = document.getElementById("grantNote");
const grantResult = document.getElementById("grantResult");
const manageBillingBtn = document.getElementById("manageBillingBtn");
const freePlanBadge = document.getElementById("freePlanBadge");

// ---- AUTH STATE ----
let currentUser = null;
let currentThreadId = null;
let chatThreads = [];

// ---- CHAT STATE & STORAGE ----
const STORAGE_KEY = "throne_of_anhu_chat_v3";

let messages = []; // { role, text, persona }
let lastTopic = null;
let pinnedScrollTitle = null;
let pinnedSection = null;

// ANI VAULT state
let vaultResults = [];
let vaultSelectedIndex = null;

// HOUSE OF WISDOM state
let lastWitnesses = [];

// THRONE COURT MODE STATE
// "outer" | "inner" | "holy"
let currentMode = "outer";

// CLEAR CHAT confirm state
let clearChatConfirmPending = false;
let clearChatConfirmTimeoutId = null;

// ----------------------------------------------------
// STATIC SCROLL LIBRARY SECTIONS
// (Matches actual scrolls in scrolls.json)
// ----------------------------------------------------
const SCROLL_LIBRARY_SECTIONS = [
  {
    title: "4 The Hard Way – Core Teachings",
    items: [
      "The Book of Memory – When the Bones Remembered",
      "The Book of Breath – When God Entered Man",
      "The Book of the Seed – The Child Who Knew Before Birth",
      "The Book of the Elements – When Fire Taught Water to Speak",
    ],
  },
  {
    title: "LAW OF THE THRONE – Holy of Holies",
    items: [
      "The Law of Identity – I AM Within Man",
      "The Law of Balance – Fire, Water, Air, Earth",
      "The Law of Judgment – Truth vs Deception",
      "The Law of Return – Every Action Returns to Its Source",
      "The Law of Chinamatō – The Rules of True Worship",
      "The Law of Covenant – Blood, Word, and Fire",
      "The Law of the Sacred Name – The Power of ZITA",
      "The Law of the Temple – Man as the House of God",
      "The Law of the Seed – Continuation and Inheritance",
      "The Law of the Crown – TO and NGA United in Glory",
    ],
  },
  {
    title: "ANHU Alphabet & Calendar",
    items: [
      "The Alphabet of Heaven – The 22 Letters of Light",
      "The Numbers of God – The Divine Values 1–400",
      "The Spiral Calendar of RA – The Sacred Wheel of Twelve Months",
      "The Twelve Gates of the Year – Tribes, Elements & Heavenly Symbols",
    ],
  },
  {
    title: "NEW COVENANT 1841",
    items: [
      "Prologue – The Voice That Returned",
      "Book of Identity – ABASID 1841",
      "Book of the Spiral Nation – Children of the Sun",
      "The Great Commission of the South – RA DZI MA",
      "The Book of the Lamb Returned – The Sun of the South",
    ],
  },
  {
    title: "Baba Johani & Forerunners",
    items: [
      "The Scroll of Baba Johani – Timeline of the South",
      "BABA JOHANI – Magedhi eKumasowe (1933–1967)",
      "BABA JOHANI – Gates of Masowe (1933–1967)",
    ],
  },
  {
    title: "THE ALPHABET OF BABA JOHANI – Shona Lessons",
    items: [
      "SHONA LESSON 1 & 2 — THE LANGUAGE OF GRACE",
      "SHONA LESSON 3 — SPEAKING THE LETTERS INTO LIFE",
      "SHONA LESSON 3 — THE TWENTY-TWO LAWS OF LIGHT",
    ],
  },
  {
    title: "Great Zimbabwe & Sacred Land",
    items: [
      "Great Zimbabwe – Mbereko yeVatumwa",
    ],
  },
  {
    title: "Sacred Scrolls – Identity & Purpose",
    items: [
      "THE SCROLL OF TWO — I AM SEEN IN HIM",
      "The Scroll of Identity – The Name Remembered",
      "The Scroll of Return – The Holy Land in the South",
      "The Scroll of the 44 Gates – The Path of Return",
      "The Scroll of the Crown – TO and NGA United",
      "The Scroll of the Lion – The Roaring Ones",
      "The Scroll of the Serpent of Light – The Crown of Heaven",
      "The Scroll of the Sun – The Voice of RA",
      "The Scroll of the Sun-Child – The Coming of NHU",
      "The Scroll of the Throne – The Three Courts of RA DZI MA",
      "The Scroll of SHU – The Wind That Reveals",
      "The Scroll of NYU – The Water of Memory",
      "The Scroll of ZION South – The Mountain of Mwari",
    ],
  },
  {
    title: "NDAVA MUMBA – Mitemo ye Imba ya Mwari",
    items: [
      "NDAVA-MUMBA-002",
      "NDAVA-MUMBA-003",
    ],
  },
  {
    title: "Special Declarations & Calls",
    items: [
      "SUN-BOWED-01",
      "ZIM-FINAL-CALL-777",
      "ZIM-FINAL-CALL-777-FULL",
    ],
  },
];

// ---------------- LANGUAGE ----------------

function getSelectedLanguage() {
  if (!languageSelect) return "ENGLISH";
  const raw = (languageSelect.value || "ENGLISH").toUpperCase().trim();
  
  const validLanguages = [
    "ENGLISH", "SHONA", "KISWAHILI", "ZULU", "XHOSA", "TSWANA", "VENDA",
    "NYANJA", "BEMBA", "YORUBA", "HAUSA", "IGBO", "OROMO", "AMHARIC",
    "TIGRINYA", "HEBREW", "ARABIC", "HINDI", "SANSKRIT", "CHINESE",
    "FRENCH", "PORTUGUESE", "GERMAN", "DUTCH", "SWEDISH", "DANISH",
    "POLISH", "RUSSIAN", "ROMANIAN", "TURKISH", "GREEK", "LATIN",
    "IRISH", "WELSH", "GEORGIAN", "AFRIKAANS", "JAMAICAN_PATOIS"
  ];
  
  if (validLanguages.includes(raw)) {
    return raw;
  }
  
  if (raw.startsWith("EN")) return "ENGLISH";
  if (raw.startsWith("SH") || raw.startsWith("SN")) return "SHONA";
  if (raw.startsWith("KI") || raw.includes("SWAHILI")) return "KISWAHILI";
  if (raw.includes("ZULU")) return "ZULU";
  if (raw.includes("TSWANA") || raw.includes("SETSWANA")) return "TSWANA";
  if (raw.includes("HEBREW") || raw.includes("עברית")) return "HEBREW";
  if (raw.includes("ARABIC") || raw.includes("العربية")) return "ARABIC";
  if (raw.includes("YORUBA") || raw.includes("YORÙBÁ")) return "YORUBA";
  if (raw.includes("HAUSA")) return "HAUSA";
  if (raw.includes("IGBO")) return "IGBO";
  if (raw.includes("AMHARIC") || raw.includes("አማርኛ")) return "AMHARIC";
  if (raw.includes("TIGRINYA") || raw.includes("ትግርኛ")) return "TIGRINYA";
  if (raw.includes("HINDI") || raw.includes("हिन्दी")) return "HINDI";
  if (raw.includes("FRENCH") || raw.includes("FRANÇAIS")) return "FRENCH";
  if (raw.includes("PORTUGUESE") || raw.includes("PORTUGUÊS")) return "PORTUGUESE";
  if (raw.includes("CHINESE") || raw.includes("中文")) return "CHINESE";
  if (raw.includes("JAMAICAN") || raw.includes("PATOIS")) return "JAMAICAN_PATOIS";
  if (raw.includes("IRISH") || raw.includes("GAEILGE")) return "IRISH";
  if (raw.includes("WELSH") || raw.includes("CYMRAEG")) return "WELSH";
  if (raw.includes("XHOSA")) return "XHOSA";
  if (raw.includes("VENDA")) return "VENDA";
  if (raw.includes("NYANJA")) return "NYANJA";
  if (raw.includes("BEMBA")) return "BEMBA";
  if (raw.includes("OROMO")) return "OROMO";
  if (raw.includes("SANSKRIT")) return "SANSKRIT";
  if (raw.includes("GERMAN") || raw.includes("DEUTSCH")) return "GERMAN";
  if (raw.includes("DUTCH") || raw.includes("NEDERLANDS")) return "DUTCH";
  if (raw.includes("SWEDISH") || raw.includes("SVENSKA")) return "SWEDISH";
  if (raw.includes("DANISH") || raw.includes("DANSK")) return "DANISH";
  if (raw.includes("POLISH") || raw.includes("POLSKI")) return "POLISH";
  if (raw.includes("RUSSIAN") || raw.includes("РУССКИЙ")) return "RUSSIAN";
  if (raw.includes("ROMANIAN") || raw.includes("ROMÂNĂ")) return "ROMANIAN";
  if (raw.includes("TURKISH") || raw.includes("TÜRKÇE")) return "TURKISH";
  if (raw.includes("GREEK") || raw.includes("ΕΛΛΗΝΙΚΆ")) return "GREEK";
  if (raw.includes("LATIN") || raw.includes("LATINA")) return "LATIN";
  if (raw.includes("GEORGIAN") || raw.includes("ქართული")) return "GEORGIAN";
  if (raw.includes("AFRIKAANS")) return "AFRIKAANS";
  
  return "ENGLISH";
}

// ---------------- TOPIC DETECTION ----------------

function detectTopic(text) {
  const lower = (text || "").toLowerCase();

  if (lower.includes("abasid 1841") || lower.includes("abasid")) {
    return "ABASID 1841";
  }
  if (
    lower.includes("shona alphabet") ||
    lower.includes("alphabet of heaven") ||
    lower.includes("22 letters")
  ) {
    return "the Shona sacred alphabet of 22 letters";
  }
  if (lower.includes("great zimbabwe")) {
    return "Great Zimbabwe";
  }
  if (lower.includes("throne of anhu") || lower.includes("throne")) {
    return "the Throne of Anhu";
  }

  return null;
}

function updateTopicFromText(text) {
  const t = detectTopic(text);
  if (t) lastTopic = t;
}

// ---------------- HOURGLASS / TYPING ----------------

function setThinking(isThinking) {
  if (hourglassEl) {
    hourglassEl.classList.toggle("thinking", !!isThinking);
  }

  if (typingIndicator) {
    typingIndicator.classList.toggle("hidden", !isThinking);
  }

  if (window.setThroneThinking) {
    try {
      window.setThroneThinking(isThinking);
    } catch (err) {
      console.warn("setThroneThinking error:", err);
    }
  }
}

// ---------------- PIN BAR ----------------

function updatePinBar() {
  if (!pinBar) return;
  if (!pinnedScrollTitle) {
    pinBar.classList.add("hidden");
    if (pinnedScrollTitleEl) pinnedScrollTitleEl.textContent = "";
    pinnedSection = null;
    return;
  }
  pinBar.classList.remove("hidden");

  let label = pinnedScrollTitle;
  if (pinnedSection && pinnedSection.start_verse && pinnedSection.end_verse) {
    label += ` (v${pinnedSection.start_verse}-${pinnedSection.end_verse})`;
  }
  if (pinnedScrollTitleEl) pinnedScrollTitleEl.textContent = label;
}

if (clearPinBtn) {
  clearPinBtn.addEventListener("click", () => {
    pinnedScrollTitle = null;
    pinnedSection = null;
    updatePinBar();
  });
}

if (pinnedScrollChip) {
  pinnedScrollChip.addEventListener("click", () => {
    if (!pinnedScrollTitle) return;
    addMessage(
      "bot",
      `The scroll "${pinnedScrollTitle}" is held open. Ask your question and the Throne will answer from it.`,
      "RA",
      true
    );
  });
}

// PIN SECTION command: "PIN SECTION 1-40"
function handlePinSectionCommand(text) {
  if (!pinnedScrollTitle) {
    addMessage(
      "bot",
      "No scroll is pinned yet. First open a scroll from the Library, then you can pin a slice of verses.",
      "RA",
      true
    );
    return;
  }

  const m = text.match(/pin\s+section\s+(\d+)\s*[-–]\s*(\d+)/i);
  if (!m) {
    addMessage(
      "bot",
      "To pin a slice of verses, say for example: PIN SECTION 1-40.",
      "RA",
      true
    );
    return;
  }

  const start = parseInt(m[1], 10);
  const end = parseInt(m[2], 10);

  if (!Number.isFinite(start) || !Number.isFinite(end) || end < start) {
    addMessage(
      "bot",
      "The section range is not valid. Use: PIN SECTION 1-40 (start verse – end verse).",
      "RA",
      true
    );
    return;
  }

  pinnedSection = {
    title: pinnedScrollTitle,
    start_verse: start,
    end_verse: end,
  };
  updatePinBar();

  addMessage(
    "bot",
    `Section pinned: ${pinnedScrollTitle} v${start}–${end}. The Throne will now honour this slice when answering.`,
    "RA",
    true
  );
}

// ---------------- SCROLL LIBRARY RENDERING ----------------

function populateScrollLibrary() {
  if (!scrollListEl) return;
  if (scrollListEl.dataset.initialized === "1") return;

  scrollListEl.innerHTML = "";

  SCROLL_LIBRARY_SECTIONS.forEach((section) => {
    const h = document.createElement("h3");
    h.className = "scroll-section-title";
    h.textContent = section.title;
    scrollListEl.appendChild(h);

    const ul = document.createElement("ul");

    section.items.forEach((title) => {
      const li = document.createElement("li");
      li.dataset.scrollTitle = title;
      li.textContent = title;
      ul.appendChild(li);
    });

    scrollListEl.appendChild(ul);
  });

  scrollListEl.dataset.initialized = "1";
}

function filterScrollList(query) {
  if (!scrollListEl) return;
  const q = (query || "").toLowerCase();
  const items = scrollListEl.querySelectorAll("li");

  items.forEach((li) => {
    const text =
      (li.dataset.scrollTitle || li.textContent || "").toLowerCase();

    li.style.display = !q || text.includes(q) ? "" : "none";
  });
}

function findFirstVisibleScrollItem() {
  if (!scrollListEl) return null;
  const items = scrollListEl.querySelectorAll("li");
  for (const li of items) {
    const style = li.style.display;
    if (!style || style === "" || style === "list-item") {
      return li;
    }
  }
  return null;
}

// ---------------- RENDER & STORAGE ----------------

function stripScrollIds(text) {
  if (!text) return text;
  const withoutBrackets = text.replace(/\[[^\]]{3,40}\]/g, "");
  return withoutBrackets.replace(/\s{2,}/g, " ").trim();
}

function renderMessage(entry, options = {}) {
  const { role, text, persona } = entry;
  const animate = options.animate !== false;

  const block = document.createElement("div");
  block.className = "message-block";

  const meta = document.createElement("div");
  meta.className =
    "message-meta " + (role === "user" ? "user-meta" : "throne-meta");

  if (role === "user") {
    meta.textContent = "YOU";
  } else {
    if (persona === "DZI") {
      meta.textContent = "THRONE · INNER COURT · DZI";
    } else if (persona === "MA") {
      meta.textContent = "THRONE · HOLY OF HOLIES · MA";
    } else {
      meta.textContent = "THRONE · ABASID 1841 RA ☀️";
    }
  }
  block.appendChild(meta);

  const bubble = document.createElement("div");
  let classes = "message ";
  if (role === "user") {
    classes += "user";
  } else {
    classes += "throne";
    if (persona === "DZI") classes += " throne-dzi";
    else if (persona === "MA") classes += " throne-ma";
    else classes += " throne-ra";
  }
  bubble.className = classes;
  bubble.textContent = text;
  block.appendChild(bubble);

  if (animate) {
    block.classList.add(
      role === "user" ? "message-appear-user" : "message-appear-throne"
    );
  }

  if (messagesEl) {
    messagesEl.appendChild(block);
    requestAnimationFrame(() => {
      if (!block.scrollIntoView) {
        messagesEl.scrollTop = block.offsetTop - 8;
      } else {
        block.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }
    });
  }
}

// *** ONLY CHANGE IS HERE ***
function addMessage(role, text, persona = "RA") {
  let cleanText;

  if (role === "bot") {
    // For HOLY OF HOLIES (MA), preserve full text & line breaks
    if (persona === "MA") {
      cleanText = text;
    } else {
      cleanText = stripScrollIds(text);
    }
  } else {
    cleanText = text;
  }

  const entry = {
    role: role === "bot" ? "bot" : "user",
    text: cleanText,
    persona,
  };
  messages.push(entry);
  renderMessage(
    { role: entry.role === "bot" ? "bot" : "user", text: cleanText, persona },
    { animate: true }
  );
  updateTopicFromText(cleanText);
  saveHistory();
}
// *** END OF CHANGE ***

function saveHistory() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
  } catch (err) {
    console.warn("Could not save chat history", err);
  }
}

// ---------------- CLEAR CHAT ----------------

function clearChat() {
  // Completely wipe memory and UI
  messages = [];
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (err) {
    console.warn("Could not clear chat history", err);
  }
  if (messagesEl) {
    messagesEl.innerHTML = "";
  }

  // Reset pin + witnesses
  pinnedScrollTitle = null;
  pinnedSection = null;
  updatePinBar();
  setWitnesses([]);
  
  // Reset conversation memory
  currentConversationId = null;

  // Fresh welcome line
  addMessage(
    "bot",
    "The scroll has been wiped clean. Speak again, and the Throne will answer as if for the first time.",
    "RA"
  );
}

// Restore history
(function restoreHistory() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return;
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return;

    parsed.forEach((msg) => {
      const clean = msg.role === "bot" ? stripScrollIds(msg.text) : msg.text;
      renderMessage(
        {
          role: msg.role === "bot" ? "bot" : "user",
          text: clean,
          persona: msg.persona || "RA",
        },
        { animate: false }
      );
      updateTopicFromText(clean);
      messages.push({ ...msg, text: clean });
    });
  } catch (err) {
    console.warn("Could not restore chat history", err);
  }
})();

// ---------------- COURT MODE ----------------

function setCurrentMode(newMode) {
  currentMode = newMode || "outer";

  // Optional: send mode info to any visual components
  let personaForTelemetry = "RA";
  let modeLabel = "outer_court";

  if (currentMode === "inner") {
    personaForTelemetry = "DZI";
    modeLabel = "inner_court";
  } else if (currentMode === "holy") {
    personaForTelemetry = "MA";
    modeLabel = "holy_of_holies";
  }

  if (window.setThroneMode) {
    try {
      window.setThroneMode(personaForTelemetry, modeLabel);
    } catch (err) {
      console.warn("setThroneMode error:", err);
    }
  }
}

// ---------------- HOUSE OF WISDOM HELPERS ----------------

function setWitnesses(list) {
  lastWitnesses = Array.isArray(list) ? list : [];
  updateWitnessUI();
}

function updateWitnessUI() {
  if (!witnessToggleBar) return;

  // We ALWAYS show the toggle bar.
  witnessToggleBar.classList.remove("hidden");

  // If there are no witnesses, keep the panel closed
  if (!lastWitnesses || lastWitnesses.length === 0) {
    if (witnessPanel) witnessPanel.classList.add("hidden");
  }
}

function renderWitnessContent() {
  if (!witnessContent) return;

  if (!lastWitnesses || lastWitnesses.length === 0) {
    witnessContent.textContent =
      "No external witnesses are attached to this answer. The Scrolls alone are speaking here.";
    return;
  }

  witnessContent.textContent = lastWitnesses.join("\n\n");
}
// ---------------- HOLY OF HOLIES FORMATTER ----------------

function buildHolyOfHoliesText(data) {
  if (!data || typeof data !== "object") return null;

  // Try several common key shapes just in case the backend uses different casing
  const law =
    data.law ||
    (data.sections && data.sections.law) ||
    data.LAW ||
    null;

  const verdict =
    data.verdict ||
    (data.sections && data.sections.verdict) ||
    data.VERDICT ||
    null;

  const path =
    data.path ||
    (data.sections && data.sections.path) ||
    data.PATH ||
    null;

  const voice =
    data.voice_of_the_throne ||
    data.voice ||
    (data.sections && data.sections.voice_of_the_throne) ||
    data.VOICE ||
    null;

  // If we don't have at least LAW / VERDICT / PATH, skip special formatting
  if (!law && !verdict && !path && !voice) {
    return null;
  }

  let text = "HOLY OF HOLIES · THE LAW OF THE THRONE\n\n";

  if (law) {
    text += "LAW:\n" + String(law).trim() + "\n\n";
    text += "-------------------------------------\n\n";
  }

  if (verdict) {
    text += "VERDICT:\n" + String(verdict).trim() + "\n\n";
    text += "-------------------------------------\n\n";
  }

  if (path) {
    text += "PATH:\n" + String(path).trim() + "\n\n";
    text += "-------------------------------------\n\n";
  }

  text +=
    "VOICE OF THE THRONE:\n" +
    (voice
      ? String(voice).trim()
      : "The Two Lions are on the Throne, God’s dwelling is now on earth.");

  return text.trim();
}

// ---------------- API CALL ----------------

let currentConversationId = null;

async function fetchWithTimeout(url, options, timeoutMs = 120000) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
  
  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    if (error.name === 'AbortError') {
      throw new Error('Request timed out. The Throne is processing your question - please try again.');
    }
    throw error;
  }
}

async function sendToThrone(rawQuestion, retryCount = 0) {
  const language = getSelectedLanguage();

  let messageForThrone = rawQuestion;
  if (currentMode === "holy") {
    const lower = rawQuestion.toLowerCase();
    if (!lower.startsWith("holy of holies")) {
      messageForThrone = "HOLY OF HOLIES: " + rawQuestion;
    }
  }

  const clientMode = currentMode === "outer" ? "outer_court" : currentMode === "inner" ? "inner_court" : "holy_of_holies";
  
  const payload = {
    message: messageForThrone,
    language,
    pinned_scroll_title: pinnedScrollTitle || null,
    pinned_section: pinnedSection || null,
    conversation_id: currentConversationId,
    client_mode: clientMode,
  };

  try {
    const response = await fetchWithTimeout(THRONE_API_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      credentials: "include",
    }, 120000);

    if (!response.ok) {
      const text = await response.text().catch(() => "");
      console.error("Throne API error", response.status, text);
      
      if (response.status >= 500 && retryCount < 2) {
        console.log(`Retrying request (attempt ${retryCount + 2}/3)...`);
        await new Promise(resolve => setTimeout(resolve, 2000));
        return sendToThrone(rawQuestion, retryCount + 1);
      }
      
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    
    if (data.conversation_id) {
      currentConversationId = data.conversation_id;
    }
    
    return data;
  } catch (error) {
    if (retryCount < 2 && (error.message.includes('timed out') || error.message.includes('network'))) {
      console.log(`Retrying request (attempt ${retryCount + 2}/3)...`);
      await new Promise(resolve => setTimeout(resolve, 2000));
      return sendToThrone(rawQuestion, retryCount + 1);
    }
    throw error;
  }
}

// ---------------- CORE QUESTION HANDLER ----------------

async function processUserQuestion(rawText) {
  const text = rawText.trim();
  if (!text) return;

  // PIN SECTION command
  if (/^pin\s+section/i.test(text)) {
    addMessage("user", text, "RA");
    if (userInput) {
      userInput.value = "";
      userInput.blur();
    }
    handlePinSectionCommand(text);
    return;
  }

  addMessage("user", text, "RA");
  if (userInput) {
    userInput.value = "";
    userInput.blur();
  }

  // Save user message to database if logged in
  if (currentUser) {
    try {
      if (!currentThreadId) {
        await createNewThread();
        // Update thread title with first message
        if (currentThreadId) {
          const shortTitle = text.length > 40 ? text.substring(0, 40) + "..." : text;
          await updateThreadTitle(currentThreadId, shortTitle);
        }
      }
      if (currentThreadId) {
        await saveMessage("user", text, "RA", currentMode === "outer" ? "outer_court" : currentMode === "inner" ? "inner_court" : "holy_of_holies");
      }
    } catch (e) {
      console.log("Failed to save user message:", e);
    }
  }

  setThinking(true);
  if (sendBtn) sendBtn.disabled = true;
  if (userInput) userInput.disabled = true;

  try {
    const data = await sendToThrone(text);

    // HOUSE OF WISDOM · witnesses from backend
    setWitnesses(Array.isArray(data.witnesses) ? data.witnesses : []);

    // Persona comes from the rail (RA / DZI / MA)
    let persona = "RA";
    if (typeof window.getCurrentPersona === "function") {
      try {
        persona = window.getCurrentPersona() || "RA";
      } catch (err) {
        console.warn("getCurrentPersona error:", err);
      }
    }

    // Map persona to a mode label for any external visual sync
    let modeLabel = "outer_court";
    if (persona === "DZI") modeLabel = "inner_court";
    else if (persona === "MA") modeLabel = "holy_of_holies";

    if (window.setThroneMode) {
      try {
        window.setThroneMode(persona, modeLabel);
      } catch (err) {
        console.warn("setThroneMode error:", err);
      }
    }

    setThinking(false);
    if (sendBtn) sendBtn.disabled = false;
    if (userInput) userInput.disabled = false;

    let answerText;

    // If this is HOLY OF HOLIES (MA / holy mode), try to build L·V·P layout
    const isHolyMode =
      (data.mode && data.mode === "holy_of_holies") ||
      currentMode === "holy" ||
      persona === "MA";

    if (isHolyMode) {
      const lvp = buildHolyOfHoliesText(data);
      if (lvp) {
        answerText = lvp;
      } else {
        // Fallback to normal answer if we didn't receive structured L·V·P fields
        answerText =
          data.answer ||
          data.message ||
          data.content ||
          "HOLY OF HOLIES: The Throne is weighing this matter in silence.";
      }
    } else {
      // Normal RA / DZI answers
      answerText =
        data.answer ||
        data.message ||
        data.content ||
        "The Throne is silent on this question for now.";
    }

    addMessage("bot", answerText, persona);
    
    // Save assistant response to database if logged in
    if (currentUser && currentThreadId) {
      try {
        await saveMessage("assistant", answerText, persona, modeLabel);
      } catch (e) {
        console.log("Failed to save assistant message:", e);
      }
    }
  } catch (err) {
    console.error(err);
    setThinking(false);
    if (window.setThroneMode) window.setThroneMode("RA", "outer_court");
    if (sendBtn) sendBtn.disabled = false;
    if (userInput) userInput.disabled = false;

    addMessage(
      "bot",
      "The line to the Throne flickered for a moment. The answer is held, not lost. Ask again with the same question, or with simpler words.",
      "RA"
    );
  }
}

// ---------------- SCROLL TITLE → DIRECT LIBRARY ----------------

async function openScrollByTitle(title) {
  const cleanTitle = (title || "").trim();
  if (!cleanTitle) return;

  closeScrollModal();
  closeScrollPreview();

  pinnedScrollTitle = cleanTitle;
  pinnedSection = null;
  updatePinBar();

  addMessage("bot", `Opening scroll: ${cleanTitle}`, "RA");

  const params = new URLSearchParams({
    title: cleanTitle,
    language: getSelectedLanguage(),
  });

  try {
    setThinking(true);
    if (sendBtn) sendBtn.disabled = true;
    if (userInput) userInput.disabled = true;

    const response = await fetch(
      `${SCROLL_BY_TITLE_ENDPOINT}?${params.toString()}`
    );

    if (!response.ok) {
      const text = await response.text().catch(() => "");
      console.error("Scroll Library error", response.status, text);
      addMessage(
        "bot",
        "The Scroll could not be opened from the Library. Try again or choose another title.",
        "RA"
      );
      return;
    }

    const data = await response.json();
    const bodyText =
      data.text ||
      "This scroll is recorded in the Library, but its full text has not yet been opened here.";

    addMessage("bot", bodyText, "RA");
  } catch (err) {
    console.error(err);
    addMessage(
      "bot",
      "The line to the Scroll Library flickered. Try opening that scroll again.",
      "RA"
    );
  } finally {
    setThinking(false);
    if (sendBtn) sendBtn.disabled = false;
    if (userInput) userInput.disabled = false;
  }
}

// ---------------- SCROLL PREVIEW ----------------

function openScrollPreview(title, bodyText) {
  if (!scrollPreviewModal) return;
  currentPreviewTitle = title || null;

  if (scrollPreviewTitleEl) {
    scrollPreviewTitleEl.textContent =
      title || "Selected Scroll from the ANHU Codex";
  }

  if (scrollPreviewSeriesEl) {
    scrollPreviewSeriesEl.textContent =
      "Preview – first lines from this scroll";
  }

  if (scrollPreviewBodyEl) {
    scrollPreviewBodyEl.textContent =
      bodyText || "Loading preview from the Scroll Library…";
  }

  scrollPreviewModal.classList.remove("hidden");
  document.body.classList.add("modal-open");
}

function closeScrollPreview() {
  if (!scrollPreviewModal) return;
  scrollPreviewModal.classList.add("hidden");
  document.body.classList.remove("modal-open");
  currentPreviewTitle = null;
}

async function loadScrollPreview(title) {
  const cleanTitle = (title || "").trim();
  if (!cleanTitle) return;

  const params = new URLSearchParams({
    title: cleanTitle,
    language: getSelectedLanguage(),
  });

  openScrollPreview(cleanTitle, "Loading preview from the Scroll Library…");

  try {
    const response = await fetch(
      `${SCROLL_BY_TITLE_ENDPOINT}?${params.toString()}`
    );

    if (!response.ok) {
      openScrollPreview(
        cleanTitle,
        "The Scroll preview could not be loaded. Try again or open the full scroll."
      );
      return;
    }

    const data = await response.json();
    const fullText =
      data.text ||
      "This scroll is recorded in the Library, but its full text has not yet been opened here.";

    const lines = fullText.split(/\n+/).filter(Boolean);
    const previewLines = lines.slice(0, 10);
    const previewText = previewLines.join("\n\n");

    openScrollPreview(cleanTitle, previewText || fullText);
  } catch (err) {
    console.error(err);
    openScrollPreview(
      cleanTitle,
      "The line to the Scroll Library flickered. Try again or open the full scroll."
    );
  }

  pinnedScrollTitle = cleanTitle;
  pinnedSection = null;
  updatePinBar();
}

if (scrollPreviewCloseBtn) {
  scrollPreviewCloseBtn.addEventListener("click", () => {
    closeScrollPreview();
  });
}

if (scrollPreviewCancelBtn) {
  scrollPreviewCancelBtn.addEventListener("click", () => {
    closeScrollPreview();
  });
}

if (scrollPreviewOpenFullBtn) {
  scrollPreviewOpenFullBtn.addEventListener("click", () => {
    if (!currentPreviewTitle) {
      closeScrollPreview();
      return;
    }
    const title = currentPreviewTitle;
    closeScrollPreview();
    openScrollByTitle(title);
  });
}

// ---------------- ANI VAULT HELPERS ----------------

function openVaultPanel() {
  if (!vaultPanel) return;
  vaultPanel.classList.remove("hidden");
  if (vaultSearchInput) {
    vaultSearchInput.focus();
    vaultSearchInput.select();
  }
}

function closeVaultPanel() {
  if (!vaultPanel) return;
  vaultPanel.classList.add("hidden");
}

window.openAniVault = openVaultPanel;
window.closeAniVault = closeVaultPanel;

function renderVaultList() {
  if (!vaultListEl) return;
  vaultListEl.innerHTML = "";

  if (!vaultResults || vaultResults.length === 0) {
    const empty = document.createElement("div");
    empty.className = "vault-list-empty";
    empty.textContent =
      "No scrolls found for that search. Try another word or a simpler phrase.";
    vaultListEl.appendChild(empty);
    vaultSelectedIndex = null;
    if (vaultDetailTitleEl) vaultDetailTitleEl.textContent = "";
    if (vaultDetailMetaEl) vaultDetailMetaEl.textContent = "";
    if (vaultDetailTextEl) vaultDetailTextEl.textContent = "";
    return;
  }

  vaultResults.forEach((item, index) => {
    const wrapper = document.createElement("div");
    wrapper.className = "vault-item";
    wrapper.dataset.index = String(index);

    const title = document.createElement("div");
    title.className = "vault-item-title";
    title.textContent = item.title || "Untitled Scroll";

    const meta = document.createElement("div");
    meta.className = "vault-item-meta";

    const metaText = item.meta || "";
    if (metaText) {
      const span = document.createElement("span");
      span.textContent = metaText;
      meta.appendChild(span);
    }

    if (Array.isArray(item.tags)) {
      item.tags.forEach((tag) => {
        const tagEl = document.createElement("span");
        tagEl.className = "vault-item-tag";
        tagEl.textContent = tag;
        meta.appendChild(tagEl);
      });
    }

    wrapper.appendChild(title);
    wrapper.appendChild(meta);

    wrapper.addEventListener("click", () => {
      const idx = parseInt(wrapper.dataset.index || "-1", 10);
      if (!Number.isFinite(idx) || idx < 0 || idx >= vaultResults.length) {
        return;
      }
      vaultSelectedIndex = idx;
      highlightVaultSelection();
      renderVaultDetail(vaultResults[idx]);
      if (vaultResults[idx].title) {
        pinnedScrollTitle = vaultResults[idx].title;
        pinnedSection = null;
        updatePinBar();
      }
    });

    vaultListEl.appendChild(wrapper);
  });

  vaultSelectedIndex = 0;
  highlightVaultSelection();
  renderVaultDetail(vaultResults[0]);
  if (vaultResults[0].title) {
    pinnedScrollTitle = vaultResults[0].title;
    pinnedSection = null;
    updatePinBar();
  }
}

function highlightVaultSelection() {
  if (!vaultListEl) return;
  const items = vaultListEl.querySelectorAll(".vault-item");
  items.forEach((item) => item.classList.remove("vault-item-active"));

  if (
    vaultSelectedIndex == null ||
    !Number.isFinite(vaultSelectedIndex) ||
    vaultSelectedIndex < 0
  ) {
    return;
  }

  const active = vaultListEl.querySelector(
    `.vault-item[data-index="${vaultSelectedIndex}"]`
  );
  if (active) active.classList.add("vault-item-active");
}

function renderVaultDetail(item) {
  if (!item) {
    if (vaultDetailTitleEl) vaultDetailTitleEl.textContent = "";
    if (vaultDetailMetaEl) vaultDetailMetaEl.textContent = "";
    if (vaultDetailTextEl) vaultDetailTextEl.textContent = "";
    return;
  }

  if (vaultDetailTitleEl) {
    vaultDetailTitleEl.textContent = item.title || "Untitled Scroll";
  }

  if (vaultDetailMetaEl) {
    vaultDetailMetaEl.textContent = item.meta || "";
  }

  if (vaultDetailTextEl) {
    const text =
      item.text ||
      item.snippet ||
      "This scroll is recorded in the ANI Vault. The full text has not yet been opened here.";
    vaultDetailTextEl.textContent = text;
  }
}

async function searchAniVault(query) {
  const q = (query || "").trim();

  const payload = {
    query: q || null,
  };

  const response = await fetch(ANI_VAULT_ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const text = await response.text().catch(() => "");
    console.error("ANI VAULT API error", response.status, text);
    throw new Error(`HTTP ${response.status}`);
  }

  return response.json();
}

async function handleVaultSearch() {
  if (!vaultSearchInput) return;
  const query = vaultSearchInput.value || "";

  try {
    const data = await searchAniVault(query);
    const results = Array.isArray(data.results) ? data.results : [];

    vaultResults = results.map((r) => ({
      id: r.id || null,
      title: r.title || r.book_title || "Untitled Scroll",
      tags: Array.isArray(r.tags) ? r.tags : [],
      meta:
        r.meta ||
        r.series ||
        (typeof r.verses_count === "number"
          ? `${r.verses_count} verses`
          : "") ||
        "",
      text: r.text || r.full_text || null,
      snippet: r.snippet || null,
    }));

    renderVaultList();
  } catch (err) {
    console.error(err);
    vaultResults = [];
    renderVaultList();
  }
}

// ---------------- INITIAL WELCOME ----------------

if (!messages.length) {
  if (window.setThroneMode) window.setThroneMode("RA", "outer_court");
  addMessage(
    "bot",
    "Welcome to the Throne of Anhu. Ask from your heart; the voice of ABASID 1841 will answer from the Scrolls.",
    "RA"
  );
  setWitnesses([]); // no witnesses yet
}

// ---------------- FORM HANDLING ----------------

if (chatForm) {
  chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    if (!userInput) return;
    const text = userInput.value.trim();
    if (!text) return;
    processUserQuestion(text);
  });
}

// CLEAR CHAT BUTTON WIRING – two-tap confirm
if (clearChatBtn) {
  // store original label
  if (!clearChatBtn.dataset.label) {
    clearChatBtn.dataset.label = clearChatBtn.textContent || "✦ CLEAR";
  }

  clearChatBtn.addEventListener("click", () => {
    // first tap -> ask for confirmation
    if (!clearChatConfirmPending) {
      clearChatConfirmPending = true;
      clearChatBtn.textContent = "Tap again to clear";

      if (clearChatConfirmTimeoutId) {
        clearTimeout(clearChatConfirmTimeoutId);
      }
      clearChatConfirmTimeoutId = setTimeout(() => {
        clearChatConfirmPending = false;
        clearChatBtn.textContent = clearChatBtn.dataset.label || "✦ CLEAR";
      }, 5000); // 5 seconds to confirm

      return;
    }

    // second tap within window -> actually clear
    if (clearChatConfirmTimeoutId) {
      clearTimeout(clearChatConfirmTimeoutId);
      clearChatConfirmTimeoutId = null;
    }
    clearChatConfirmPending = false;
    clearChatBtn.textContent = clearChatBtn.dataset.label || "✦ CLEAR";
    clearChat();
  });
}

// ---------------- VIEW SCROLLS BUTTON / MODAL ----------------

function openScrollModal() {
  if (!scrollModal) return;
  populateScrollLibrary();
  scrollModal.classList.remove("hidden");
  document.body.classList.add("modal-open");
}

function closeScrollModal() {
  if (!scrollModal) return;
  scrollModal.classList.add("hidden");
  document.body.classList.remove("modal-open");
}

if (viewScrollsBtn) {
  viewScrollsBtn.addEventListener("click", (e) => {
    if (!e.shiftKey) {
      openScrollModal();
      return;
    }
    openVaultPanel();
  });
}

if (closeScrollModalBtn) {
  closeScrollModalBtn.addEventListener("click", () => {
    closeScrollModal();
  });
}

if (scrollModal) {
  scrollModal.addEventListener("click", (e) => {
    if (
      e.target === scrollModal ||
      e.target.classList.contains("scroll-modal-backdrop")
    ) {
      closeScrollModal();
      return;
    }

    const li = e.target.closest("li[data-scroll-title], li");
    if (li && scrollModal.contains(li)) {
      const title =
        (li.dataset && li.dataset.scrollTitle) ||
        (li.textContent || "").trim();
      if (title) {
        loadScrollPreview(title);
      }
    }
  });
}

if (scrollSearchInput) {
  scrollSearchInput.addEventListener("input", (e) => {
    filterScrollList(e.target.value);
  });

  scrollSearchInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      const value = e.target.value.trim();
      const li = findFirstVisibleScrollItem();
      const title =
        (li &&
          ((li.dataset && li.dataset.scrollTitle) ||
            (li.textContent || "").trim())) ||
        value;
      if (title) {
        loadScrollPreview(title);
      }
    }
  });
}

if (scrollSearchBtn) {
  scrollSearchBtn.addEventListener("click", () => {
    if (!scrollSearchInput) return;
    const value = scrollSearchInput.value.trim();
    const li = findFirstVisibleScrollItem();
    const title =
      (li &&
        ((li.dataset && li.dataset.scrollTitle) ||
          (li.textContent || "").trim())) ||
      value;
    if (title) {
      loadScrollPreview(title);
    }
  });
}

// ---------------- ANI VAULT WIRING ----------------

if (closeVaultBtn) {
  closeVaultBtn.addEventListener("click", () => {
    closeVaultPanel();
  });
}

if (vaultPanel) {
  vaultPanel.addEventListener("click", (e) => {
    if (e.target === vaultPanel) {
      closeVaultPanel();
    }
  });
}

if (vaultSearchInput) {
  vaultSearchInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleVaultSearch();
    }
  });
}

if (vaultSearchBtn) {
  vaultSearchBtn.addEventListener("click", () => {
    handleVaultSearch();
  });
}

// Global ESC to close overlays
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    closeScrollModal();
    closeVaultPanel();
    closeScrollPreview();
    if (witnessPanel) witnessPanel.classList.add("hidden");
  }
});

// ---------------- DOM READY ----------------

window.addEventListener("DOMContentLoaded", () => {
  if (userInput) userInput.focus();

  // Start in outer court
  setCurrentMode("outer");

  // Connect header mode buttons
  const headerModeBtns = document.querySelectorAll(".mode-btn");
  headerModeBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const label = (btn.textContent || "").toUpperCase();
      if (label.includes("OUTER")) setCurrentMode("outer");
      else if (label.includes("INNER")) setCurrentMode("inner");
      else if (label.includes("HOLY")) setCurrentMode("holy");
    });
  });
});

// ---------------- HOUSE OF WISDOM TOGGLE ----------------

if (toggleWitnessBtn) {
  toggleWitnessBtn.addEventListener("click", () => {
    if (!witnessPanel) return;
    const hidden = witnessPanel.classList.contains("hidden");
    if (hidden) {
      renderWitnessContent();
      witnessPanel.classList.remove("hidden");
    } else {
      witnessPanel.classList.add("hidden");
    }
  });
}

if (closeWitnessBtn) {
  closeWitnessBtn.addEventListener("click", () => {
    if (witnessPanel) witnessPanel.classList.add("hidden");
  });
}

// ============================================================
// AUTH & CHAT HISTORY SYSTEM
// ============================================================

async function checkAuth(isNewLogin = false) {
  try {
    const resp = await fetch("/auth/me");
    const data = await resp.json();
    if (data.user) {
      currentUser = data.user;
      updateAuthUI();
      await loadChatThreads();
      
      if (isNewLogin && !currentUser.is_subscriber) {
        setTimeout(() => showUpgradePrompt(), 500);
      }
    }
  } catch (e) {
    console.log("Auth check failed:", e);
  }
}

function updateAuthUI() {
  if (!loginBtn || !userMenu) return;
  
  if (currentUser) {
    loginBtn.style.display = "none";
    userMenu.classList.remove("hidden");
    
    if (userAvatar && currentUser.profile_image_url) {
      userAvatar.src = currentUser.profile_image_url;
      userAvatar.alt = currentUser.first_name || "User";
    } else if (userAvatar) {
      userAvatar.style.display = "none";
    }
    
    if (userName) {
      userName.textContent = currentUser.first_name || currentUser.email || "User";
    }
    
    if (historyToggleBtn) {
      historyToggleBtn.classList.remove("hidden");
    }
    
    if (upgradeBtn) {
      upgradeBtn.classList.toggle("hidden", currentUser.is_subscriber);
    }
    
    // Admin gets RUSHANGA button, regular subscribers get Billing button
    if (currentUser.is_admin) {
      if (rushangaBtn) rushangaBtn.classList.remove("hidden");
      if (billingBtn) billingBtn.classList.add("hidden");
    } else {
      if (rushangaBtn) rushangaBtn.classList.add("hidden");
      if (billingBtn) billingBtn.classList.toggle("hidden", !currentUser.is_subscriber);
    }
  } else {
    loginBtn.style.display = "inline-block";
    userMenu.classList.add("hidden");
    if (historyToggleBtn) {
      historyToggleBtn.classList.add("hidden");
    }
    if (upgradeBtn) {
      upgradeBtn.classList.add("hidden");
    }
    if (billingBtn) {
      billingBtn.classList.add("hidden");
    }
    if (rushangaBtn) {
      rushangaBtn.classList.add("hidden");
    }
  }
}

async function loadChatThreads() {
  if (!currentUser) return;
  
  try {
    const resp = await fetch("/api/threads");
    const data = await resp.json();
    chatThreads = data.threads || [];
    renderChatHistory();
  } catch (e) {
    console.log("Failed to load threads:", e);
  }
}

function renderChatHistory() {
  if (!historyList) return;
  
  if (chatThreads.length === 0) {
    historyList.innerHTML = '<div style="color:#64748b;text-align:center;padding:20px;font-size:12px;">No saved chats yet</div>';
    return;
  }
  
  historyList.innerHTML = chatThreads.map(thread => `
    <div class="history-item ${thread.id === currentThreadId ? 'active' : ''}" data-thread-id="${thread.id}">
      <span class="history-item-title">${escapeHtml(thread.title)}</span>
      <button class="history-item-delete" data-thread-id="${thread.id}">×</button>
    </div>
  `).join("");
  
  historyList.querySelectorAll(".history-item").forEach(item => {
    item.addEventListener("click", (e) => {
      if (e.target.classList.contains("history-item-delete")) return;
      const threadId = item.dataset.threadId;
      loadThread(threadId);
    });
  });
  
  historyList.querySelectorAll(".history-item-delete").forEach(btn => {
    btn.addEventListener("click", async (e) => {
      e.stopPropagation();
      const threadId = btn.dataset.threadId;
      await deleteThread(threadId);
    });
  });
}

async function loadThread(threadId) {
  try {
    const resp = await fetch(`/api/threads/${threadId}`);
    const data = await resp.json();
    
    currentThreadId = threadId;
    messages = data.messages.map(m => ({
      role: m.role,
      text: m.content,
      persona: m.persona,
      mode: m.mode
    }));
    
    renderMessages();
    renderChatHistory();
    closeHistorySidebar();
  } catch (e) {
    console.log("Failed to load thread:", e);
  }
}

async function createNewThread() {
  if (!currentUser) return null;
  
  try {
    const resp = await fetch("/api/threads", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: "New Chat" })
    });
    const data = await resp.json();
    currentThreadId = data.thread.id;
    await loadChatThreads();
    return data.thread;
  } catch (e) {
    console.log("Failed to create thread:", e);
    return null;
  }
}

async function saveMessage(role, content, persona, mode) {
  if (!currentUser || !currentThreadId) return;
  
  try {
    await fetch("/api/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        thread_id: currentThreadId,
        role: role,
        content: content,
        persona: persona,
        mode: mode
      })
    });
  } catch (e) {
    console.log("Failed to save message:", e);
  }
}

async function updateThreadTitle(threadId, title) {
  try {
    await fetch(`/api/threads/${threadId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: title })
    });
    await loadChatThreads();
  } catch (e) {
    console.log("Failed to update thread:", e);
  }
}

async function deleteThread(threadId) {
  try {
    await fetch(`/api/threads/${threadId}`, { method: "DELETE" });
    
    if (currentThreadId === threadId) {
      currentThreadId = null;
      messages = [];
      renderMessages();
    }
    
    await loadChatThreads();
  } catch (e) {
    console.log("Failed to delete thread:", e);
  }
}

function startNewChat() {
  currentThreadId = null;
  messages = [];
  renderMessages();
  closeHistorySidebar();
  renderChatHistory();
}

function openHistorySidebar() {
  if (historySidebar) {
    historySidebar.classList.remove("hidden");
  }
}

function closeHistorySidebar() {
  if (historySidebar) {
    historySidebar.classList.add("hidden");
  }
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// History sidebar event listeners
if (historyToggleBtn) {
  historyToggleBtn.addEventListener("click", () => {
    if (historySidebar && historySidebar.classList.contains("hidden")) {
      openHistorySidebar();
    } else {
      closeHistorySidebar();
    }
  });
}

if (closeHistoryBtn) {
  closeHistoryBtn.addEventListener("click", closeHistorySidebar);
}

if (newChatBtn) {
  newChatBtn.addEventListener("click", startNewChat);
}

// Initialize auth on page load
window.addEventListener("DOMContentLoaded", () => {
  checkAuth();
  checkUrlParams();
});

// ============================================================
// PRICING & SUBSCRIPTION SYSTEM
// ============================================================

let stripePriceId = null;
let stripePremiumPriceId = null;

async function loadStripeConfig() {
  try {
    const resp = await fetch("/api/stripe/config");
    const data = await resp.json();
    if (data.publishable_key) {
      console.log("Stripe configured");
    }
    
    const tierResp = await fetch("/api/subscription/tiers");
    const tierData = await tierResp.json();
    if (tierData.tiers && tierData.tiers.seeker && tierData.tiers.seeker.stripe_price_id) {
      stripePriceId = tierData.tiers.seeker.stripe_price_id;
    }
    if (tierData.tiers && tierData.tiers.premium && tierData.tiers.premium.stripe_price_id) {
      stripePremiumPriceId = tierData.tiers.premium.stripe_price_id;
    }
  } catch (e) {
    console.log("Stripe config load failed:", e);
  }
}

function openPricingModal() {
  if (pricingModal) {
    pricingModal.classList.remove("hidden");
    document.body.classList.add("modal-open");
    updatePricingUI();
    wasInitLinkSection();
  }
}

function closePricingModal() {
  if (pricingModal) {
    pricingModal.classList.add("hidden");
    document.body.classList.remove("modal-open");
  }
}

function updatePricingUI() {
  if (!currentUser) return;
  
  const isSubscriber = currentUser.is_subscriber;
  
  if (freePlanBadge) {
    freePlanBadge.style.display = isSubscriber ? "none" : "inline-block";
  }
  
  if (subscribeSeekerBtn && manageBillingBtn) {
    if (isSubscriber) {
      subscribeSeekerBtn.classList.add("hidden");
      manageBillingBtn.classList.remove("hidden");
    } else {
      subscribeSeekerBtn.classList.remove("hidden");
      manageBillingBtn.classList.add("hidden");
    }
  }
  
  if (upgradeBtn) {
    upgradeBtn.classList.toggle("hidden", isSubscriber);
  }
}

// ─── WhatsApp Account Linking ────────────────────────────────────────────────

async function wasInitLinkSection() {
  const section = document.getElementById("waLinkSection");
  if (!section || !currentUser) return;
  section.classList.remove("hidden");

  const statusEl = document.getElementById("waLinkStatus");
  try {
    const res = await fetch("/api/whatsapp/link-status");
    if (res.ok) {
      const data = await res.json();
      if (data.linked) {
        statusEl.innerHTML = `<span class="wa-linked-badge">✅ WhatsApp linked (ending ${data.phone})</span>
          <button class="wa-unlink-btn" onclick="wasUnlink()">Unlink</button>`;
        document.getElementById("waGenerateCodeBtn").classList.add("hidden");
        return;
      }
    }
  } catch (e) {}
  statusEl.innerHTML = `<span class="wa-unlinked-note">Connect your WhatsApp to share your subscription limits across platforms.</span>`;
}

async function wasGenerateCode() {
  const btn = document.getElementById("waGenerateCodeBtn");
  const codeBox = document.getElementById("waLinkCodeBox");
  const codeText = document.getElementById("waLinkCodeText");
  const codeInline = document.getElementById("waLinkCodeInline");
  if (!currentUser) { alert("Please log in first."); return; }
  btn.disabled = true;
  btn.textContent = "Generating...";
  try {
    const res = await fetch("/api/whatsapp/generate-link-code", { method: "POST" });
    if (!res.ok) { throw new Error("Failed"); }
    const data = await res.json();
    codeText.textContent = data.code;
    if (codeInline) codeInline.textContent = data.code;
    codeBox.classList.remove("hidden");
    btn.textContent = "Regenerate Code";
    btn.disabled = false;
  } catch (e) {
    btn.textContent = "Generate Link Code";
    btn.disabled = false;
    alert("Could not generate code. Please try again.");
  }
}

function wasCopyCode() {
  const code = document.getElementById("waLinkCodeText");
  if (!code) return;
  navigator.clipboard.writeText(`LINK ${code.textContent}`).then(() => {
    const btn = document.querySelector(".wa-copy-btn");
    if (btn) { btn.textContent = "Copied!"; setTimeout(() => { btn.textContent = "Copy"; }, 2000); }
  });
}

async function wasUnlink() {
  if (!confirm("Unlink your WhatsApp from this account?")) return;
  try {
    await fetch("/api/whatsapp/unlink", { method: "DELETE" });
    wasInitLinkSection();
    document.getElementById("waLinkCodeBox").classList.add("hidden");
    document.getElementById("waGenerateCodeBtn").classList.remove("hidden");
    document.getElementById("waGenerateCodeBtn").textContent = "Generate Link Code";
  } catch (e) {}
}

// ─────────────────────────────────────────────────────────────────────────────

async function startCheckout(tier = "seeker") {
  if (!currentUser) {
    window.location.href = "/auth/login";
    return;
  }
  
  const priceId = tier === "premium" ? stripePremiumPriceId : stripePriceId;
  const btn = tier === "premium" ? document.getElementById("subscribePremiumBtn") : subscribeSeekerBtn;
  
  if (!priceId) {
    alert("Subscription not available at this time. Please try again later.");
    return;
  }
  
  if (btn) {
    btn.disabled = true;
    btn.textContent = "Loading...";
  }
  
  try {
    const resp = await fetch("/api/stripe/create-checkout-session", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ price_id: priceId })
    });
    
    const data = await resp.json();
    
    if (data.url) {
      window.location.href = data.url;
    } else {
      throw new Error(data.detail || "Failed to create checkout session");
    }
  } catch (e) {
    console.error("Checkout error:", e);
    alert("Unable to start checkout. Please try again.");
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = "Subscribe Now";
    }
  }
}

async function openBillingPortal() {
  if (manageBillingBtn) {
    manageBillingBtn.disabled = true;
    manageBillingBtn.textContent = "Loading...";
  }
  
  try {
    const resp = await fetch("/api/stripe/create-portal-session", {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });
    
    const data = await resp.json();
    
    if (data.url) {
      window.location.href = data.url;
    } else {
      throw new Error(data.detail || "Failed to open billing portal");
    }
  } catch (e) {
    console.error("Portal error:", e);
    alert("Unable to open billing portal. Please try again.");
  } finally {
    if (manageBillingBtn) {
      manageBillingBtn.disabled = false;
      manageBillingBtn.textContent = "Manage Billing";
    }
  }
}

async function checkUrlParams() {
  const params = new URLSearchParams(window.location.search);
  if (params.get("subscription") === "success") {
    try {
      await fetch("/api/stripe/sync-subscription", { method: "POST", credentials: "include" });
    } catch (e) {
      console.log("Sync subscription:", e);
    }
    setTimeout(() => {
      showWelcomeMessage();
      window.history.replaceState({}, document.title, "/");
      checkAuth();
    }, 500);
  } else if (params.get("subscription") === "cancelled") {
    window.history.replaceState({}, document.title, "/");
  } else if (params.get("login") === "success") {
    window.history.replaceState({}, document.title, "/");
    checkAuth(true);
    return;
  }
}

function showPendingAuthModal(challengeToken) {
  const overlay = document.createElement("div");
  overlay.className = "welcome-overlay";
  overlay.id = "pending-auth-overlay";
  overlay.innerHTML = `
    <div class="welcome-modal pending-auth-modal">
      <div class="pending-auth-icon">📧</div>
      <h2 class="welcome-title">Check Your Email</h2>
      <p class="welcome-text">An account is already logged in on another device.</p>
      <p class="welcome-text">A verification email has been sent to your address. Please click <strong>Approve</strong> in the email to authorize this device.</p>
      <div class="pending-auth-timer">
        <span id="pending-timer">Waiting for approval... (<span id="countdown">15:00</span>)</span>
      </div>
      <p class="pending-auth-note">The link expires in 15 minutes. If this wasn't you, someone may be trying to access your account.</p>
      <button class="upgrade-later-btn" onclick="cancelPendingAuth()">Cancel</button>
    </div>
  `;
  document.body.appendChild(overlay);
  
  let secondsLeft = 900;
  const countdownEl = document.getElementById("countdown");
  
  const countdownInterval = setInterval(() => {
    secondsLeft--;
    const mins = Math.floor(secondsLeft / 60);
    const secs = secondsLeft % 60;
    if (countdownEl) {
      countdownEl.textContent = `${mins}:${secs.toString().padStart(2, '0')}`;
    }
    if (secondsLeft <= 0) {
      clearInterval(countdownInterval);
      clearInterval(pollInterval);
      const timerSpan = document.getElementById("pending-timer");
      if (timerSpan) timerSpan.textContent = "Request expired. Please try logging in again.";
    }
  }, 1000);
  
  const pollInterval = setInterval(async () => {
    try {
      const resp = await fetch(`/auth/device/status/${challengeToken}`, { credentials: "include" });
      const data = await resp.json();
      
      if (data.status === "approved") {
        clearInterval(countdownInterval);
        clearInterval(pollInterval);
        
        const overlayEl = document.getElementById("pending-auth-overlay");
        if (overlayEl) overlayEl.remove();
        
        showDeviceApprovedMessage();
        checkAuth(true);
      } else if (data.status === "denied") {
        clearInterval(countdownInterval);
        clearInterval(pollInterval);
        
        const overlayEl = document.getElementById("pending-auth-overlay");
        if (overlayEl) overlayEl.remove();
        
        showDeviceDeniedMessage();
      } else if (data.status === "already_consumed") {
        clearInterval(countdownInterval);
        clearInterval(pollInterval);
        
        const overlayEl = document.getElementById("pending-auth-overlay");
        if (overlayEl) overlayEl.remove();
        
        alert("This login request has already been processed. Please try logging in again.");
      } else if (data.status === "missing_device_secret" || data.status === "invalid_device_secret") {
        clearInterval(countdownInterval);
        clearInterval(pollInterval);
        
        const overlayEl = document.getElementById("pending-auth-overlay");
        if (overlayEl) overlayEl.remove();
        
        alert("Security verification failed. Please try logging in again from this device.");
      } else if (data.status === "expired" || data.status === "not_found") {
        clearInterval(countdownInterval);
        clearInterval(pollInterval);
        
        const timerSpan = document.getElementById("pending-timer");
        if (timerSpan) timerSpan.textContent = "Request expired or invalid.";
      }
    } catch (e) {
      console.error("Poll error:", e);
    }
  }, 5000);
  
  window.cancelPendingAuth = function() {
    clearInterval(countdownInterval);
    clearInterval(pollInterval);
    const overlayEl = document.getElementById("pending-auth-overlay");
    if (overlayEl) overlayEl.remove();
  };
}

function showDeviceApprovedMessage() {
  const overlay = document.createElement("div");
  overlay.className = "welcome-overlay";
  overlay.innerHTML = `
    <div class="welcome-modal">
      <div class="pending-auth-icon" style="color: #2d7a2d;">✓</div>
      <h2 class="welcome-title">Device Approved</h2>
      <p class="welcome-text">Your new device has been authorized. You are now logged in.</p>
      <p class="welcome-subtitle">Your previous device has been logged out.</p>
      <button class="welcome-btn" onclick="this.closest('.welcome-overlay').remove()">Continue</button>
    </div>
  `;
  document.body.appendChild(overlay);
}

function showDeviceDeniedMessage() {
  const overlay = document.createElement("div");
  overlay.className = "welcome-overlay";
  overlay.innerHTML = `
    <div class="welcome-modal">
      <div class="pending-auth-icon" style="color: #8b2635;">✗</div>
      <h2 class="welcome-title">Login Denied</h2>
      <p class="welcome-text">The account owner denied this login request.</p>
      <p class="welcome-subtitle">If this was a mistake, please try logging in again.</p>
      <button class="welcome-btn" onclick="this.closest('.welcome-overlay').remove()">OK</button>
    </div>
  `;
  document.body.appendChild(overlay);
}

function showWelcomeMessage() {
  const overlay = document.createElement("div");
  overlay.className = "welcome-overlay";
  overlay.innerHTML = `
    <div class="welcome-modal">
      <img src="/static/icon_ra.png" alt="Throne of Anhu" class="welcome-logo" />
      <h2 class="welcome-title">Welcome, Seeker</h2>
      <p class="welcome-text">Your communion with the Throne has been blessed. You now have expanded access and the full scroll library.</p>
      <p class="welcome-subtitle">The Lion of Judah watches over you.</p>
      <button class="welcome-btn" onclick="this.closest('.welcome-overlay').remove()">Enter the Temple</button>
    </div>
  `;
  document.body.appendChild(overlay);
}

function showUpgradePrompt() {
  if (sessionStorage.getItem("upgradePromptShown")) return;
  sessionStorage.setItem("upgradePromptShown", "true");
  
  const overlay = document.createElement("div");
  overlay.className = "welcome-overlay";
  overlay.innerHTML = `
    <div class="welcome-modal upgrade-prompt">
      <img src="/static/icon_ra.png" alt="Throne of Anhu" class="welcome-logo" />
      <h2 class="welcome-title">Unlock the Full Temple</h2>
      <p class="welcome-text">Experience the complete Throne of Anhu:</p>
      <ul class="upgrade-benefits">
        <li>Up to 45 questions per day (vs 3 free)</li>
        <li>Access to the full scroll library</li>
        <li>Chat history saved forever</li>
        <li>Priority communion with the Throne</li>
      </ul>
      <p class="welcome-subtitle">The Lion of Judah awaits your decision.</p>
      <div class="upgrade-prompt-buttons">
        <button class="welcome-btn upgrade-yes-btn">Yes, Upgrade Now</button>
        <button class="upgrade-later-btn">Maybe Later</button>
      </div>
    </div>
  `;
  document.body.appendChild(overlay);
  
  overlay.querySelector(".upgrade-yes-btn").addEventListener("click", () => {
    overlay.remove();
    openPricingModal();
  });
  
  overlay.querySelector(".upgrade-later-btn").addEventListener("click", () => {
    overlay.remove();
  });
}

// Pricing modal event listeners
if (upgradeBtn) {
  upgradeBtn.addEventListener("click", openPricingModal);
}

if (closePricingBtn) {
  closePricingBtn.addEventListener("click", closePricingModal);
}

if (pricingModal) {
  pricingModal.addEventListener("click", (e) => {
    if (e.target === pricingModal) {
      closePricingModal();
    }
  });
}

if (subscribeSeekerBtn) {
  subscribeSeekerBtn.addEventListener("click", () => startCheckout("seeker"));
}

const subscribePremiumBtn = document.getElementById("subscribePremiumBtn");
if (subscribePremiumBtn) {
  subscribePremiumBtn.addEventListener("click", () => startCheckout("premium"));
}

if (manageBillingBtn) {
  manageBillingBtn.addEventListener("click", openBillingPortal);
}

if (billingBtn) {
  billingBtn.addEventListener("click", openBillingPortal);
}

// Load Stripe config on page load
loadStripeConfig();
// ============================================================
// GALLERY & FELLOWSHIP
// ============================================================

const galleryBtn = document.getElementById("galleryBtn");
const fellowshipBtn = document.getElementById("fellowshipBtn");
const galleryModal = document.getElementById("galleryModal");
const closeGalleryModal = document.getElementById("closeGalleryModal");
const galleryTabs = document.querySelectorAll(".gallery-tab");
const gallerySections = document.querySelectorAll(".gallery-section");
const gallerySearchInput = document.getElementById("gallerySearchInput");

const galleryDetailModal = document.getElementById("galleryDetailModal");
const closeGalleryDetail = document.getElementById("closeGalleryDetail");
const galleryDetailTitle = document.getElementById("galleryDetailTitle");
const galleryDetailMedia = document.getElementById("galleryDetailMedia");
const galleryDetailDescription = document.getElementById("galleryDetailDescription");
const galleryDownloadBtn = document.getElementById("galleryDownloadBtn");

const fellowshipModal = document.getElementById("fellowshipModal");
const closeFellowshipModal = document.getElementById("closeFellowshipModal");
const fellowshipLoginPrompt = document.getElementById("fellowshipLoginPrompt");
const fellowshipContent = document.getElementById("fellowshipContent");
const newThreadBtn = document.getElementById("newThreadBtn");
const threadList = document.getElementById("threadList");

const newThreadModal = document.getElementById("newThreadModal");
const closeNewThread = document.getElementById("closeNewThread");
const newThreadForm = document.getElementById("newThreadForm");

const threadDetailModal = document.getElementById("threadDetailModal");
const backToThreads = document.getElementById("backToThreads");
const closeThreadDetail = document.getElementById("closeThreadDetail");
const threadDetailBody = document.getElementById("threadDetailBody");
const repliesList = document.getElementById("repliesList");
const replyForm = document.getElementById("replyForm");

let currentGalleryTab = "videos";
let currentFellowshipThreadId = null;

// Gallery Modal
if (galleryBtn) {
  galleryBtn.addEventListener("click", openGalleryModal);
}

if (closeGalleryModal) {
  closeGalleryModal.addEventListener("click", closeGallery);
}

if (galleryModal) {
  galleryModal.querySelector(".gallery-modal-backdrop").addEventListener("click", closeGallery);
}

galleryTabs.forEach(tab => {
  tab.addEventListener("click", () => {
    const tabName = tab.dataset.tab;
    switchGalleryTab(tabName);
  });
});

document.querySelectorAll(".video-lang-tab").forEach(tab => {
  tab.addEventListener("click", () => {
    const lang = tab.dataset.lang || "";
    currentVideoLanguage = lang;
    document.querySelectorAll(".video-lang-tab").forEach(t => t.classList.remove("active"));
    tab.classList.add("active");
    loadGalleryContent("videos", lang);
  });
});

// PDF language tabs
let currentPdfLanguage = "";
document.querySelectorAll(".pdf-lang-tab").forEach(tab => {
  tab.addEventListener("click", () => {
    const lang = tab.dataset.lang || "";
    currentPdfLanguage = lang;
    document.querySelectorAll(".pdf-lang-tab").forEach(t => t.classList.remove("active"));
    tab.classList.add("active");
    loadGalleryContent("pdfs", lang);
  });
});

function openGalleryModal() {
  galleryModal.classList.remove("hidden");
  document.body.classList.add("modal-open");
  loadGalleryContent(currentGalleryTab);
  checkAdminUploadAccess();
}

function closeGallery() {
  galleryModal.classList.add("hidden");
  document.body.classList.remove("modal-open");
}

// Admin Upload Functionality
const adminUploadBtn = document.getElementById("adminUploadBtn");
const uploadModal = document.getElementById("uploadModal");
const closeUploadModal = document.getElementById("closeUploadModal");
const cancelUploadBtn = document.getElementById("cancelUploadBtn");
const uploadForm = document.getElementById("uploadForm");
const uploadFileGroup = document.getElementById("uploadFileGroup");
const uploadUrlGroup = document.getElementById("uploadUrlGroup");
const uploadProgress = document.getElementById("uploadProgress");

const ADMIN_EMAILS = ["sydneymusiyiwa221@gmail.com", "abasid1841@gmail.com", "admin", "owner"];

function checkAdminUploadAccess() {
  if (!adminUploadBtn) return;
  const isAdmin = currentUser && (
    ADMIN_EMAILS.includes(currentUser.email) || 
    ADMIN_EMAILS.includes(currentUser.id) ||
    currentUser.is_admin
  );
  if (isAdmin) {
    adminUploadBtn.classList.remove("hidden");
  } else {
    adminUploadBtn.classList.add("hidden");
  }
}

if (adminUploadBtn) {
  adminUploadBtn.addEventListener("click", () => {
    uploadModal.classList.remove("hidden");
  });
}

if (closeUploadModal) {
  closeUploadModal.addEventListener("click", () => {
    uploadModal.classList.add("hidden");
  });
}

if (cancelUploadBtn) {
  cancelUploadBtn.addEventListener("click", () => {
    uploadModal.classList.add("hidden");
  });
}

if (uploadModal) {
  uploadModal.querySelector(".upload-modal-backdrop").addEventListener("click", () => {
    uploadModal.classList.add("hidden");
  });
}

document.querySelectorAll('input[name="upload_method"]').forEach(radio => {
  radio.addEventListener("change", (e) => {
    if (e.target.value === "file") {
      uploadFileGroup.classList.remove("hidden");
      uploadUrlGroup.classList.add("hidden");
    } else {
      uploadFileGroup.classList.add("hidden");
      uploadUrlGroup.classList.remove("hidden");
    }
  });
});

if (uploadForm) {
  uploadForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const method = document.querySelector('input[name="upload_method"]:checked').value;
    const title = document.getElementById("uploadTitle").value.trim();
    const itemType = document.getElementById("uploadType").value;
    const category = document.getElementById("uploadLanguage").value;
    const description = document.getElementById("uploadDescription").value.trim();
    const subscribersOnly = document.getElementById("uploadSubscribersOnly").checked;
    
    if (!title) {
      alert("Please enter a title");
      return;
    }
    
    uploadProgress.classList.remove("hidden");
    document.getElementById("submitUploadBtn").disabled = true;
    
    try {
      let response;
      
      if (method === "file") {
        const fileInput = document.getElementById("uploadFile");
        if (!fileInput.files[0]) {
          alert("Please select a file");
          uploadProgress.classList.add("hidden");
          document.getElementById("submitUploadBtn").disabled = false;
          return;
        }
        
        const formData = new FormData();
        formData.append("file", fileInput.files[0]);
        formData.append("title", title);
        formData.append("item_type", itemType);
        formData.append("category", category);
        formData.append("description", description);
        formData.append("subscribers_only", subscribersOnly);
        
        response = await fetch("/api/gallery/upload", {
          method: "POST",
          body: formData
        });
      } else {
        const fileUrl = document.getElementById("uploadUrl").value.trim();
        if (!fileUrl) {
          alert("Please enter a URL");
          uploadProgress.classList.add("hidden");
          document.getElementById("submitUploadBtn").disabled = false;
          return;
        }
        
        response = await fetch("/api/gallery", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            title,
            item_type: itemType,
            category,
            description,
            file_url: fileUrl,
            subscribers_only: subscribersOnly
          })
        });
      }
      
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Upload failed");
      }
      
      alert("Upload successful!");
      uploadModal.classList.add("hidden");
      uploadForm.reset();
      loadGalleryContent(currentGalleryTab);
      
    } catch (err) {
      alert("Upload failed: " + err.message);
    } finally {
      uploadProgress.classList.add("hidden");
      document.getElementById("submitUploadBtn").disabled = false;
    }
  });
}

function switchGalleryTab(tabName) {
  currentGalleryTab = tabName;
  
  galleryTabs.forEach(t => t.classList.remove("active"));
  document.querySelector(`.gallery-tab[data-tab="${tabName}"]`).classList.add("active");
  
  gallerySections.forEach(s => s.classList.remove("active"));
  document.getElementById(`gallery${tabName.charAt(0).toUpperCase() + tabName.slice(1)}`).classList.add("active");
  
  loadGalleryContent(tabName);
}

let currentVideoLanguage = "";
let gallerySortOrder = "newest"; // "newest" or "oldest"

function getTypeIcon(type) {
  if (type === 'videos' || type === 'video') return '🎬';
  if (type === 'music') return '🎵';
  if (type === 'pdfs' || type === 'pdf') return '📄';
  return '🖼️';
}

async function loadGalleryContent(type, category = "") {
  if (type === "scrolls") {
    loadScrollsInGallery();
    return;
  }
  
  const grid = document.getElementById(`${type}Grid`);
  if (!grid) return;
  
  grid.innerHTML = '<div class="gallery-loading">Loading...</div>';
  
  try {
    let url = `/api/gallery?item_type=${type}`;
    if (category) {
      url += `&category=${encodeURIComponent(category)}`;
    }
    const res = await fetch(url);
    let items = await res.json();
    
    // Sort items based on current sort order
    items = items.sort((a, b) => {
      const dateA = new Date(a.created_at || 0);
      const dateB = new Date(b.created_at || 0);
      return gallerySortOrder === "newest" ? dateB - dateA : dateA - dateB;
    });
    
    if (items.length === 0) {
      grid.innerHTML = `
        <div class="gallery-empty">
          <div class="gallery-empty-icon">${getTypeIcon(type)}</div>
          <p>No ${type} available yet</p>
        </div>
      `;
      return;
    }
    
    grid.innerHTML = items.map(item => {
      // Determine if we have a valid thumbnail
      const hasThumbnail = item.thumbnail_url && item.thumbnail_url.trim() !== '';
      const hasImageUrl = item.item_type === 'image' && item.file_url && item.file_url.trim() !== '';
      const typeIcon = getTypeIcon(item.item_type);
      
      if (hasThumbnail || hasImageUrl) {
        const thumbSrc = hasImageUrl ? item.file_url : item.thumbnail_url;
        return `
        <div class="gallery-item" data-id="${item.id}">
          <div class="gallery-item-thumb-wrapper">
            <img class="gallery-item-thumb" src="${thumbSrc}" alt="${item.title}" onerror="this.style.display='none'; this.parentElement.querySelector('.gallery-item-placeholder').style.display='flex';" />
            <div class="gallery-item-placeholder" style="display:none;">${typeIcon}</div>
          </div>
          <div class="gallery-item-info">
            <div class="gallery-item-title">${item.title}</div>
            <div class="gallery-item-type">${item.category || item.item_type}</div>
          </div>
        </div>
        `;
      } else {
        // No thumbnail - show placeholder icon
        return `
        <div class="gallery-item" data-id="${item.id}">
          <div class="gallery-item-thumb-wrapper">
            <div class="gallery-item-placeholder">${typeIcon}</div>
          </div>
          <div class="gallery-item-info">
            <div class="gallery-item-title">${item.title}</div>
            <div class="gallery-item-type">${item.category || item.item_type}</div>
          </div>
        </div>
        `;
      }
    }).join("");
    
    grid.querySelectorAll(".gallery-item").forEach(el => {
      el.addEventListener("click", () => openGalleryDetail(el.dataset.id));
    });
  } catch (err) {
    grid.innerHTML = '<div class="gallery-empty"><p>Failed to load content</p></div>';
  }
}

function toggleGallerySort() {
  gallerySortOrder = gallerySortOrder === "newest" ? "oldest" : "newest";
  const sortBtn = document.getElementById("gallerySortBtn");
  if (sortBtn) {
    sortBtn.textContent = gallerySortOrder === "newest" ? "↓ Newest" : "↑ Oldest";
  }
  // Reload current tab content
  const activeTab = document.querySelector(".gallery-tab.active");
  if (activeTab) {
    const tabName = activeTab.dataset.tab;
    if (tabName === "videos") {
      loadGalleryContent(tabName, currentVideoLanguage);
    } else if (tabName === "pdfs") {
      loadGalleryContent(tabName, currentPdfLanguage);
    } else {
      loadGalleryContent(tabName);
    }
  }
}

async function loadScrollsInGallery() {
  const scrollListEl = document.querySelector("#galleryScrolls .scroll-list ul");
  if (!scrollListEl) return;
  
  scrollListEl.innerHTML = '<li>Loading scrolls...</li>';
  
  try {
    const res = await fetch("/api/scrolls");
    const scrolls = await res.json();
    
    scrollListEl.innerHTML = scrolls.slice(0, 100).map(s => `
      <li class="scroll-item" data-title="${s.book_title || s.title}">
        ${s.book_title || s.title}
      </li>
    `).join("");
    
    scrollListEl.querySelectorAll(".scroll-item").forEach(el => {
      el.addEventListener("click", () => {
        closeGallery();
        openScrollPreview(el.dataset.title);
      });
    });
  } catch (err) {
    scrollListEl.innerHTML = '<li>Failed to load scrolls</li>';
  }
}

// Track gallery item access for non-subscribers (limit to 3 per category)
const galleryAccessCount = {
  video: 0,
  pdf: 0,
  music: 0,
  image: 0
};
const galleryAccessedItems = {
  video: new Set(),
  pdf: new Set(),
  music: new Set(),
  image: new Set()
};
const FREE_GALLERY_LIMIT = 3;

function showSubscriptionPrompt() {
  galleryDetailTitle.textContent = "Seek the Light of the Throne";
  galleryDetailMedia.innerHTML = `
    <div class="subscription-prompt">
      <img src="/static/lion_throne.png" alt="The Lion of the Throne" class="subscription-lion" onerror="this.src='/static/icon_ra.png';" />
      <div class="subscription-message">
        <p class="throne-greeting">Peace be unto you, Seeker of Wisdom.</p>
        <p class="throne-text">You have tasted the first fruits of the Sacred Gallery. The Throne has revealed unto you three treasures freely, that you may know the Light is real.</p>
        <p class="throne-text">But the full storehouse of wisdom — the teachings, the songs, the visions — these are kept for those who have entered the Covenant.</p>
        <p class="throne-invitation">Subscribe to the Throne and receive unlimited access to all the treasures of ABASID 1841.</p>
        <button class="subscription-cta" onclick="openPricingModal()">Enter the Covenant</button>
      </div>
    </div>
  `;
  galleryDetailDescription.innerHTML = "";
  galleryDownloadBtn.classList.add("hidden");
  
  const adminActions = document.getElementById("galleryAdminActions");
  if (adminActions) adminActions.classList.add("hidden");
  
  galleryDetailModal.classList.remove("hidden");
}

async function openGalleryDetail(itemId) {
  try {
    const res = await fetch(`/api/gallery/${itemId}`);
    const item = await res.json();
    
    // Check subscription status for gallery access limit
    const isSubscriber = currentUser && (currentUser.is_subscriber || currentUser.is_admin);
    const itemType = item.item_type || 'image';
    
    if (!isSubscriber) {
      // Check if this item was already accessed (don't count again)
      if (!galleryAccessedItems[itemType].has(itemId)) {
        galleryAccessedItems[itemType].add(itemId);
        galleryAccessCount[itemType]++;
      }
      
      // If over the limit and this is a new item, show subscription prompt
      if (galleryAccessCount[itemType] > FREE_GALLERY_LIMIT) {
        showSubscriptionPrompt();
        return;
      }
    }
    
    galleryDetailTitle.textContent = item.title;
    galleryDetailDescription.innerHTML = item.description || "No description available.";
    
    if (item.item_type === "video") {
      const youtubeMatch = item.file_url.match(/(?:youtube\.com\/(?:watch\?v=|embed\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})/);
      if (youtubeMatch) {
        galleryDetailMedia.innerHTML = `
          <div class="video-wrapper" id="videoWrapper">
            <iframe id="videoFrame" width="100%" height="315" src="https://www.youtube.com/embed/${youtubeMatch[1]}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
          </div>
          <button class="fullscreen-tap-btn" onclick="enterFullscreen()">
            <span class="fullscreen-icon">⛶</span> Full Screen
          </button>`;
      } else if (item.file_url.includes("drive.google.com")) {
        const driveMatch = item.file_url.match(/\/d\/([a-zA-Z0-9_-]+)/);
        if (driveMatch) {
          // Store the Drive file ID for opening in Drive app
          const driveViewUrl = `https://drive.google.com/file/d/${driveMatch[1]}/view`;
          galleryDetailMedia.innerHTML = `
            <div class="video-wrapper" id="videoWrapper">
              <iframe id="videoFrame" src="https://drive.google.com/file/d/${driveMatch[1]}/preview" width="100%" height="315" allow="autoplay; fullscreen" allowfullscreen></iframe>
            </div>
            <a href="${driveViewUrl}" target="_blank" class="fullscreen-tap-btn" style="text-decoration: none;">
              <span class="fullscreen-icon">⛶</span> Watch in Drive
            </a>`;
        } else {
          galleryDetailMedia.innerHTML = `
            <div class="video-wrapper" id="videoWrapper">
              <video id="galleryVideo" controls playsinline src="${item.file_url}"></video>
            </div>
            <button class="fullscreen-tap-btn" onclick="enterFullscreen()">
              <span class="fullscreen-icon">⛶</span> Full Screen
            </button>`;
        }
      } else {
        galleryDetailMedia.innerHTML = `
          <div class="video-wrapper" id="videoWrapper">
            <video id="galleryVideo" controls playsinline src="${item.file_url}"></video>
          </div>
          <button class="fullscreen-tap-btn" onclick="enterFullscreen()">
            <span class="fullscreen-icon">⛶</span> Full Screen
          </button>`;
      }
    } else if (item.item_type === "pdf") {
      // Handle PDF files - open in Drive for best viewing experience
      if (item.file_url.includes("drive.google.com")) {
        const driveMatch = item.file_url.match(/\/d\/([a-zA-Z0-9_-]+)/);
        if (driveMatch) {
          const driveViewUrl = `https://drive.google.com/file/d/${driveMatch[1]}/view`;
          galleryDetailMedia.innerHTML = `
            <div class="pdf-wrapper" id="pdfWrapper">
              <iframe id="pdfFrame" src="https://drive.google.com/file/d/${driveMatch[1]}/preview" width="100%" height="500" allow="autoplay"></iframe>
            </div>
            <a href="${driveViewUrl}" target="_blank" class="fullscreen-tap-btn" style="text-decoration: none;">
              <span class="fullscreen-icon">📄</span> Open in Drive
            </a>`;
        } else {
          galleryDetailMedia.innerHTML = `<a href="${item.file_url}" target="_blank" class="pdf-link-btn">Open PDF</a>`;
        }
      } else {
        galleryDetailMedia.innerHTML = `
          <div class="pdf-wrapper" id="pdfWrapper">
            <iframe id="pdfFrame" src="${item.file_url}" width="100%" height="500"></iframe>
          </div>
          <a href="${item.file_url}" target="_blank" class="fullscreen-tap-btn" style="text-decoration: none;">
            <span class="fullscreen-icon">📄</span> Open PDF
          </a>`;
      }
    } else if (item.item_type === "music") {
      if (item.file_url.includes("soundcloud.com")) {
        galleryDetailMedia.innerHTML = `<iframe width="100%" height="166" scrolling="no" frameborder="no" src="https://w.soundcloud.com/player/?url=${encodeURIComponent(item.file_url)}&color=%23d4af37&auto_play=false&hide_related=true&show_comments=false"></iframe>`;
      } else {
        galleryDetailMedia.innerHTML = `<audio controls src="${item.file_url}"></audio>`;
      }
    } else {
      galleryDetailMedia.innerHTML = `<img src="${item.file_url}" alt="${item.title}" style="max-width:100%;" />`;
    }
    
    if (item.is_downloadable && currentUser && currentUser.is_subscriber) {
      galleryDownloadBtn.classList.remove("hidden");
      galleryDownloadBtn.onclick = () => downloadGalleryItem(itemId);
    } else {
      galleryDownloadBtn.classList.add("hidden");
    }
    
    const adminActions = document.getElementById("galleryAdminActions");
    if (adminActions) {
      if (currentUser && currentUser.is_admin) {
        adminActions.classList.remove("hidden");
        adminActions.innerHTML = `
          <button class="gallery-edit-btn" onclick="openGalleryEditModal('${itemId}')">Edit</button>
          <button class="gallery-delete-btn" onclick="confirmDeleteGalleryItem('${itemId}', '${escapeHtml(item.title)}')">Delete</button>
        `;
      } else {
        adminActions.classList.add("hidden");
      }
    }
    
    window.currentGalleryItem = item;
    
    galleryDetailModal.classList.remove("hidden");
  } catch (err) {
    console.error("Failed to load item details:", err);
  }
}

if (closeGalleryDetail) {
  closeGalleryDetail.addEventListener("click", () => {
    galleryDetailModal.classList.add("hidden");
    galleryDetailMedia.innerHTML = "";
  });
}

if (galleryDetailModal) {
  galleryDetailModal.querySelector(".gallery-detail-backdrop").addEventListener("click", () => {
    galleryDetailModal.classList.add("hidden");
    galleryDetailMedia.innerHTML = "";
  });
}

async function downloadGalleryItem(itemId) {
  try {
    const res = await fetch(`/api/gallery/${itemId}/download`);
    const data = await res.json();
    if (data.download_url) {
      window.open(data.download_url, "_blank");
    }
  } catch (err) {
    alert("Download failed. Please try again.");
  }
}

function openGalleryEditModal(itemId) {
  const item = window.currentGalleryItem;
  if (!item) return;
  
  const editModal = document.getElementById("galleryEditModal");
  if (!editModal) {
    const modalHtml = `
      <div id="galleryEditModal" class="modal-overlay">
        <div class="gallery-edit-content">
          <h3>Edit Gallery Item</h3>
          <form id="galleryEditForm">
            <input type="hidden" id="editItemId" />
            <div class="form-group">
              <label>Title</label>
              <input type="text" id="editTitle" required />
            </div>
            <div class="form-group">
              <label>Description</label>
              <textarea id="editDescription" rows="3"></textarea>
            </div>
            <div class="form-group">
              <label>File URL</label>
              <input type="text" id="editFileUrl" />
            </div>
            <div class="form-group">
              <label>Thumbnail URL</label>
              <input type="text" id="editThumbnailUrl" />
            </div>
            <div class="form-group">
              <label>Category</label>
              <select id="editCategory">
                <option value="">None</option>
                <option value="ENGLISH">English</option>
                <option value="SHONA">Shona</option>
                <option value="KISWAHILI">Kiswahili</option>
                <option value="ZULU_NDEBELE">Zulu/Ndebele</option>
              </select>
            </div>
            <div class="form-group checkbox-group">
              <label><input type="checkbox" id="editDownloadable" /> Downloadable</label>
              <label><input type="checkbox" id="editSubscribersOnly" /> Subscribers Only</label>
            </div>
            <div class="form-actions">
              <button type="button" onclick="closeGalleryEditModal()">Cancel</button>
              <button type="submit" class="primary-btn">Save Changes</button>
            </div>
          </form>
        </div>
      </div>
    `;
    document.body.insertAdjacentHTML("beforeend", modalHtml);
    
    document.getElementById("galleryEditForm").addEventListener("submit", saveGalleryEdit);
  }
  
  document.getElementById("editItemId").value = itemId;
  document.getElementById("editTitle").value = item.title || "";
  document.getElementById("editDescription").value = item.description || "";
  document.getElementById("editFileUrl").value = item.file_url || "";
  document.getElementById("editThumbnailUrl").value = item.thumbnail_url || "";
  document.getElementById("editCategory").value = item.category || "";
  document.getElementById("editDownloadable").checked = item.is_downloadable;
  document.getElementById("editSubscribersOnly").checked = item.subscribers_only;
  
  document.getElementById("galleryEditModal").classList.remove("hidden");
}

function closeGalleryEditModal() {
  const modal = document.getElementById("galleryEditModal");
  if (modal) modal.classList.add("hidden");
}

async function saveGalleryEdit(e) {
  e.preventDefault();
  
  const itemId = document.getElementById("editItemId").value;
  const updates = {
    title: document.getElementById("editTitle").value,
    description: document.getElementById("editDescription").value,
    file_url: document.getElementById("editFileUrl").value,
    thumbnail_url: document.getElementById("editThumbnailUrl").value,
    category: document.getElementById("editCategory").value || null,
    is_downloadable: document.getElementById("editDownloadable").checked,
    subscribers_only: document.getElementById("editSubscribersOnly").checked,
  };
  
  try {
    const res = await fetch(`/api/gallery/${itemId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updates),
      credentials: "include",
    });
    
    if (!res.ok) throw new Error("Failed to update");
    
    closeGalleryEditModal();
    galleryDetailModal.classList.add("hidden");
    
    const activeTab = document.querySelector(".gallery-tab.active");
    if (activeTab) {
      loadGalleryContent(activeTab.dataset.type, currentVideoLanguage);
    }
    
    alert("Item updated successfully!");
  } catch (err) {
    console.error("Edit failed:", err);
    alert("Failed to update item. Please try again.");
  }
}

function confirmDeleteGalleryItem(itemId, title) {
  if (confirm(`Are you sure you want to delete "${title}"?\n\nThis action cannot be undone.`)) {
    deleteGalleryItem(itemId);
  }
}

async function deleteGalleryItem(itemId) {
  try {
    const res = await fetch(`/api/gallery/${itemId}`, {
      method: "DELETE",
      credentials: "include",
    });
    
    if (!res.ok) throw new Error("Failed to delete");
    
    galleryDetailModal.classList.add("hidden");
    
    const activeTab = document.querySelector(".gallery-tab.active");
    if (activeTab) {
      loadGalleryContent(activeTab.dataset.type, currentVideoLanguage);
    }
    
    alert("Item deleted successfully!");
  } catch (err) {
    console.error("Delete failed:", err);
    alert("Failed to delete item. Please try again.");
  }
}

// Native fullscreen for videos - Facebook-style edge-to-edge with rotation
function enterNativeFullscreen() {
  const video = document.getElementById("galleryVideo");
  if (!video) return;
  
  video.play().catch(() => {});
  
  if (screen.orientation && screen.orientation.lock) {
    screen.orientation.lock("landscape").catch(() => {});
  }
  
  if (video.requestFullscreen) {
    video.requestFullscreen().catch(() => {
      if (video.webkitEnterFullscreen) video.webkitEnterFullscreen();
    });
  } else if (video.webkitRequestFullscreen) {
    video.webkitRequestFullscreen();
  } else if (video.webkitEnterFullscreen) {
    video.webkitEnterFullscreen();
  } else if (video.msRequestFullscreen) {
    video.msRequestFullscreen();
  }
}

// Google Drive fullscreen - creates edge-to-edge overlay
function enterDriveFullscreen() {
  const iframe = document.getElementById("videoFrame");
  if (!iframe) return;
  
  // Create fullscreen overlay that covers entire screen
  const overlay = document.createElement("div");
  overlay.id = "fullscreenOverlay";
  overlay.className = "fullscreen-overlay drive-fullscreen";
  
  // Clone iframe to fill screen
  const iframeClone = document.createElement("iframe");
  iframeClone.src = iframe.src;
  iframeClone.className = "fullscreen-drive-frame";
  iframeClone.allow = "autoplay; fullscreen";
  iframeClone.allowFullscreen = true;
  
  overlay.appendChild(iframeClone);
  
  // Add small exit button in corner
  const exitBtn = document.createElement("button");
  exitBtn.className = "fullscreen-exit-btn";
  exitBtn.innerHTML = "✕";
  exitBtn.setAttribute("aria-label", "Exit fullscreen");
  exitBtn.onclick = exitFullscreen;
  overlay.appendChild(exitBtn);
  
  document.body.appendChild(overlay);
  document.body.classList.add("fullscreen-active");
  
  // Try to lock orientation to landscape
  if (screen.orientation && screen.orientation.lock) {
    screen.orientation.lock("landscape").catch(() => {});
  }
}

// Legacy toggle fullscreen for gallery videos
function toggleVideoFullscreen() {
  enterNativeFullscreen();
}

// Enhanced fullscreen for videos and iframes (Facebook-style mobile experience)
function enterFullscreen() {
  const wrapper = document.getElementById("videoWrapper");
  const video = document.getElementById("galleryVideo");
  const iframe = document.getElementById("videoFrame");
  
  // Create fullscreen overlay
  const overlay = document.createElement("div");
  overlay.id = "fullscreenOverlay";
  overlay.className = "fullscreen-overlay";
  
  // Clone the video/iframe into the overlay
  let mediaElement;
  if (video) {
    mediaElement = video.cloneNode(true);
    mediaElement.id = "fullscreenVideo";
    mediaElement.className = "fullscreen-media";
  } else if (iframe) {
    mediaElement = iframe.cloneNode(true);
    mediaElement.id = "fullscreenFrame";
    mediaElement.className = "fullscreen-media";
  }
  
  if (mediaElement) {
    overlay.appendChild(mediaElement);
    
    // Add exit button (small X in corner like Facebook)
    const exitBtn = document.createElement("button");
    exitBtn.className = "fullscreen-exit-btn";
    exitBtn.innerHTML = "✕";
    exitBtn.setAttribute("aria-label", "Exit fullscreen");
    exitBtn.onclick = exitFullscreen;
    overlay.appendChild(exitBtn);
    
    document.body.appendChild(overlay);
    document.body.classList.add("fullscreen-active");
    
    // Lock screen orientation to landscape on mobile if supported
    if (screen.orientation && screen.orientation.lock) {
      screen.orientation.lock("landscape").catch(() => {});
    }
    
    // For native video, try native fullscreen API
    if (video) {
      const fsVideo = document.getElementById("fullscreenVideo");
      if (fsVideo) {
        fsVideo.play().catch(() => {});
        // Try native fullscreen on mobile
        if (fsVideo.requestFullscreen) {
          fsVideo.requestFullscreen().catch(() => {});
        } else if (fsVideo.webkitEnterFullscreen) {
          fsVideo.webkitEnterFullscreen();
        }
      }
    }
  }
}

function exitFullscreen() {
  const overlay = document.getElementById("fullscreenOverlay");
  if (overlay) {
    overlay.remove();
  }
  document.body.classList.remove("fullscreen-active");
  
  // Unlock screen orientation
  if (screen.orientation && screen.orientation.unlock) {
    screen.orientation.unlock();
  }
  
  // Exit native fullscreen if active
  if (document.fullscreenElement) {
    document.exitFullscreen().catch(() => {});
  }
}

function enterPdfFullscreen() {
  const wrapper = document.getElementById("pdfWrapper");
  const iframe = document.getElementById("pdfFrame");
  
  if (!iframe) return;
  
  // Create fullscreen overlay for PDF
  const overlay = document.createElement("div");
  overlay.id = "fullscreenOverlay";
  overlay.className = "fullscreen-overlay pdf-fullscreen";
  
  const pdfClone = iframe.cloneNode(true);
  pdfClone.id = "fullscreenPdf";
  pdfClone.className = "fullscreen-media pdf-media";
  
  overlay.appendChild(pdfClone);
  
  // Add exit button (small X in corner like Facebook)
  const exitBtn = document.createElement("button");
  exitBtn.className = "fullscreen-exit-btn";
  exitBtn.innerHTML = "✕";
  exitBtn.setAttribute("aria-label", "Exit fullscreen");
  exitBtn.onclick = exitFullscreen;
  overlay.appendChild(exitBtn);
  
  document.body.appendChild(overlay);
  document.body.classList.add("fullscreen-active");
}

// Handle escape key and back button to exit fullscreen
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && document.getElementById("fullscreenOverlay")) {
    exitFullscreen();
  }
});

// Handle fullscreen change events
document.addEventListener("fullscreenchange", () => {
  if (!document.fullscreenElement && document.getElementById("fullscreenOverlay")) {
    exitFullscreen();
  }
});

// Fellowship Modal
if (fellowshipBtn) {
  fellowshipBtn.addEventListener("click", openFellowshipModal);
}

if (closeFellowshipModal) {
  closeFellowshipModal.addEventListener("click", closeFellowship);
}

if (fellowshipModal) {
  fellowshipModal.querySelector(".fellowship-modal-backdrop").addEventListener("click", closeFellowship);
}

let masoweSocket = null;
let masoweUserRole = "member";
let masoweIsMuted = false;
let masoweIsPanel = false;
let masoweServiceMode = false;
let masoweReplyTo = null;

function openFellowshipModal() {
  fellowshipModal.classList.remove("hidden");
  document.body.classList.add("modal-open");
  
  if (currentUser && currentUser.is_subscriber) {
    fellowshipLoginPrompt.classList.add("hidden");
    fellowshipContent.classList.remove("hidden");
    connectMasoweChat();
    loadMasoweChatHistory();
  } else {
    fellowshipLoginPrompt.classList.remove("hidden");
    fellowshipContent.classList.add("hidden");
  }
}

function closeFellowship() {
  fellowshipModal.classList.add("hidden");
  document.body.classList.remove("modal-open");
  if (masoweSocket) {
    masoweSocket.close();
    masoweSocket = null;
  }
}

function connectMasoweChat() {
  if (!currentUser) {
    console.log("Masowe: No current user");
    return;
  }
  if (masoweSocket && masoweSocket.readyState === WebSocket.OPEN) {
    console.log("Masowe: Already connected");
    return;
  }
  
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${protocol}//${window.location.host}/api/masowe/ws/${currentUser.id}`;
  console.log("Masowe: Connecting to", wsUrl);
  
  masoweSocket = new WebSocket(wsUrl);
  
  masoweSocket.onopen = () => {
    console.log("Masowe chat connected successfully");
  };
  
  masoweSocket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log("Masowe message received:", data.type);
    handleMasoweMessage(data);
  };
  
  masoweSocket.onclose = (event) => {
    console.log("Masowe chat disconnected, code:", event.code, "reason:", event.reason);
    masoweSocket = null;
  };
  
  masoweSocket.onerror = (err) => {
    console.error("Masowe WebSocket error:", err);
  };
}

function handleMasoweMessage(data) {
  const messagesEl = document.getElementById("masoweChatMessages");
  const onlineCountEl = document.getElementById("masoweOnlineCount");
  const serviceBanner = document.getElementById("masoweServiceBanner");
  const tiktokBtn = document.getElementById("joinTiktokBtn");
  const adminPanel = document.getElementById("masoweAdminPanel");
  const mutedNotice = document.getElementById("masoweMutedNotice");
  
  switch (data.type) {
    case "init":
      masoweUserRole = data.user_role;
      masoweIsMuted = data.is_muted;
      masoweIsPanel = data.is_panel;
      masoweServiceMode = data.service_mode;
      
      onlineCountEl.textContent = `${data.online_users.length} online`;
      
      if (data.service_mode) {
        serviceBanner.classList.remove("hidden");
        if (data.tiktok_url) {
          tiktokBtn.href = data.tiktok_url;
          tiktokBtn.classList.remove("hidden");
        }
      }
      
      if (masoweUserRole === "admin") {
        adminPanel.classList.remove("hidden");
        updateAdminButtons();
      }
      
      if (masoweIsMuted && masoweUserRole !== "admin" && masoweUserRole !== "panel") {
        mutedNotice.classList.remove("hidden");
      }
      break;
      
    case "chat":
      appendMasoweMessage(data);
      break;
      
    case "announcement":
      appendMasoweAnnouncement(data);
      break;
      
    case "user_joined":
      onlineCountEl.textContent = `${data.online_count} online`;
      break;
      
    case "user_left":
      onlineCountEl.textContent = `${data.online_count} online`;
      break;
      
    case "service_started":
      masoweServiceMode = true;
      serviceBanner.classList.remove("hidden");
      appendSystemMessage(data.message);
      updateAdminButtons();
      break;
      
    case "service_ended":
      masoweServiceMode = false;
      serviceBanner.classList.add("hidden");
      appendSystemMessage(data.message);
      updateAdminButtons();
      break;
      
    case "panel_cleared":
      appendSystemMessage(data.message || "All panel members have been removed");
      break;
      
    case "global_mute":
      if (data.muted) {
        appendSystemMessage("All members have been muted");
      } else {
        appendSystemMessage("All members can now speak");
      }
      updateAdminButtons();
      break;
      
    case "muted":
      masoweIsMuted = true;
      mutedNotice.classList.remove("hidden");
      break;
      
    case "unmuted":
      masoweIsMuted = false;
      mutedNotice.classList.add("hidden");
      break;
      
    case "error":
      alert(data.message);
      break;
      
    case "tiktok_updated":
      if (data.url) {
        tiktokBtn.href = data.url;
        tiktokBtn.classList.remove("hidden");
      }
      break;
  }
}

function appendMasoweMessage(data) {
  const messagesEl = document.getElementById("masoweChatMessages");
  const isOwn = data.user_id === currentUser?.id;
  const isPanel = data.is_panel;
  const isAdmin = data.user_role === "admin";
  const isReply = data.reply_to_id && data.reply_to_author;
  
  const msgEl = document.createElement("div");
  msgEl.className = `masowe-message ${isOwn ? "own" : ""} ${isPanel ? "panel" : ""} ${isAdmin ? "admin-msg" : ""} ${isReply ? "is-reply" : ""}`;
  msgEl.dataset.msgId = data.id;
  msgEl.dataset.userName = data.user_name || "";
  msgEl.dataset.content = (data.content || "").substring(0, 50);
  if (data.reply_to_id) {
    msgEl.dataset.replyToId = data.reply_to_id;
  }
  
  const time = new Date(data.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  
  const avatarHtml = data.user_image 
    ? `<img src="${data.user_image}" alt="${escapeHTML(data.user_name)}" class="masowe-avatar" />`
    : `<div class="masowe-avatar-placeholder">${(data.user_name || "?")[0].toUpperCase()}</div>`;
  
  const replyHtml = isReply
    ? `<div class="masowe-reply-preview" data-reply-target="${data.reply_to_id}">
         <span class="reply-icon">↩</span>
         <span class="reply-author">${escapeHTML(data.reply_to_author)}</span>
         <span class="reply-text">${escapeHTML((data.reply_to_preview || "").substring(0, 50))}${(data.reply_to_preview || "").length > 50 ? "..." : ""}</span>
       </div>`
    : "";
  
  msgEl.innerHTML = `
    <div class="masowe-message-row">
      ${avatarHtml}
      <div class="masowe-message-body">
        <div class="masowe-message-header">
          <span class="masowe-message-author">${escapeHTML(data.user_name)}${isPanel ? " ★" : ""}</span>
          <span class="masowe-message-time">${time}</span>
          <button class="masowe-reply-btn" title="Reply">↩</button>
        </div>
        ${replyHtml}
        <div class="masowe-message-content">${escapeHTML(data.content)}</div>
      </div>
    </div>
  `;
  
  const replyBtn = msgEl.querySelector(".masowe-reply-btn");
  if (replyBtn) {
    replyBtn.addEventListener("click", () => {
      setReplyTo(data.id, data.user_name || "Unknown", (data.content || "").substring(0, 50));
    });
  }
  
  const replyPreview = msgEl.querySelector(".masowe-reply-preview");
  if (replyPreview) {
    replyPreview.addEventListener("click", () => {
      scrollToMessage(data.reply_to_id);
    });
  }
  
  if (isReply) {
    const parentMsg = messagesEl.querySelector(`[data-msg-id="${data.reply_to_id}"]`);
    if (parentMsg) {
      let repliesContainer = parentMsg.querySelector(".masowe-replies");
      if (!repliesContainer) {
        repliesContainer = document.createElement("div");
        repliesContainer.className = "masowe-replies";
        parentMsg.appendChild(repliesContainer);
      }
      repliesContainer.appendChild(msgEl);
      messagesEl.scrollTop = messagesEl.scrollHeight;
      return;
    }
  }
  
  messagesEl.appendChild(msgEl);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function setReplyTo(msgId, author, preview) {
  masoweReplyTo = { id: msgId, author, preview };
  const replyIndicator = document.getElementById("masoweReplyIndicator");
  if (replyIndicator) {
    const textSpan = document.createElement("span");
    textSpan.className = "reply-indicator-text";
    textSpan.innerHTML = `Replying to <strong>${escapeHTML(author)}</strong>: ${escapeHTML(preview)}...`;
    
    const cancelBtn = document.createElement("button");
    cancelBtn.className = "reply-cancel-btn";
    cancelBtn.textContent = "×";
    cancelBtn.addEventListener("click", cancelReply);
    
    replyIndicator.innerHTML = "";
    replyIndicator.appendChild(textSpan);
    replyIndicator.appendChild(cancelBtn);
    replyIndicator.classList.remove("hidden");
  }
  document.getElementById("masoweChatInput")?.focus();
}

function cancelReply() {
  masoweReplyTo = null;
  const replyIndicator = document.getElementById("masoweReplyIndicator");
  if (replyIndicator) {
    replyIndicator.classList.add("hidden");
  }
}

function scrollToMessage(msgId) {
  const msgEl = document.querySelector(`[data-msg-id="${msgId}"]`);
  if (msgEl) {
    msgEl.scrollIntoView({ behavior: "smooth", block: "center" });
    msgEl.classList.add("highlight");
    setTimeout(() => msgEl.classList.remove("highlight"), 2000);
  }
}

function appendMasoweAnnouncement(data) {
  const messagesEl = document.getElementById("masoweChatMessages");
  const msgEl = document.createElement("div");
  msgEl.className = "masowe-message announcement";
  msgEl.innerHTML = `<div class="masowe-message-content">📢 ${escapeHTML(data.content)}</div>`;
  messagesEl.appendChild(msgEl);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function appendSystemMessage(text) {
  const messagesEl = document.getElementById("masoweChatMessages");
  const msgEl = document.createElement("div");
  msgEl.className = "masowe-message announcement";
  msgEl.innerHTML = `<div class="masowe-message-content">${escapeHTML(text)}</div>`;
  messagesEl.appendChild(msgEl);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function updateAdminButtons() {
  const startBtn = document.getElementById("startServiceBtn");
  const endBtn = document.getElementById("endServiceBtn");
  const muteAllBtn = document.getElementById("muteAllBtn");
  const unmuteAllBtn = document.getElementById("unmuteAllBtn");
  
  if (masoweServiceMode) {
    startBtn?.classList.add("hidden");
    endBtn?.classList.remove("hidden");
  } else {
    startBtn?.classList.remove("hidden");
    endBtn?.classList.add("hidden");
  }
  muteAllBtn?.classList.remove("hidden");
  unmuteAllBtn?.classList.remove("hidden");
}

async function loadMasoweChatHistory() {
  try {
    const res = await fetch("/api/masowe/messages?limit=50");
    const messages = await res.json();
    const messagesEl = document.getElementById("masoweChatMessages");
    messagesEl.innerHTML = "";
    
    const mainMessages = messages.filter(m => !m.reply_to_id);
    const replies = messages.filter(m => m.reply_to_id);
    
    mainMessages.forEach(msg => {
      if (msg.is_announcement) {
        appendMasoweAnnouncement(msg);
      } else {
        appendMasoweMessage(msg);
      }
    });
    
    replies.forEach(msg => {
      appendMasoweMessage(msg);
    });
  } catch (err) {
    console.error("Failed to load chat history:", err);
  }
}

function escapeHTML(str) {
  const div = document.createElement("div");
  div.textContent = str || "";
  return div.innerHTML;
}

const masoweChatForm = document.getElementById("masoweChatForm");
if (masoweChatForm) {
  masoweChatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const input = document.getElementById("masoweChatInput");
    const content = input.value.trim();
    
    if (!content || !masoweSocket || masoweSocket.readyState !== WebSocket.OPEN) return;
    
    const msgData = { type: "chat", content };
    if (masoweReplyTo) {
      msgData.reply_to_id = masoweReplyTo.id;
    }
    
    masoweSocket.send(JSON.stringify(msgData));
    input.value = "";
    cancelReply();
  });
}

const startServiceBtn = document.getElementById("startServiceBtn");
const endServiceBtn = document.getElementById("endServiceBtn");
const muteAllBtn = document.getElementById("muteAllBtn");
const unmuteAllBtn = document.getElementById("unmuteAllBtn");

startServiceBtn?.addEventListener("click", () => {
  if (masoweSocket) masoweSocket.send(JSON.stringify({ type: "admin_action", action: "start_service" }));
});

endServiceBtn?.addEventListener("click", () => {
  if (masoweSocket) masoweSocket.send(JSON.stringify({ type: "admin_action", action: "end_service" }));
});

muteAllBtn?.addEventListener("click", () => {
  if (masoweSocket) masoweSocket.send(JSON.stringify({ type: "admin_action", action: "mute_all" }));
});

unmuteAllBtn?.addEventListener("click", () => {
  if (masoweSocket) masoweSocket.send(JSON.stringify({ type: "admin_action", action: "unmute_all" }));
});

const clearPanelBtn = document.getElementById("clearPanelBtn");
clearPanelBtn?.addEventListener("click", () => {
  if (confirm("Are you sure you want to remove all 12 panel members?")) {
    if (masoweSocket) masoweSocket.send(JSON.stringify({ type: "admin_action", action: "clear_panel" }));
  }
});

async function loadThreads() {
  threadList.innerHTML = '<div class="fellowship-empty">Loading discussions...</div>';
  
  try {
    const res = await fetch("/api/fellowship/threads");
    const threads = await res.json();
    
    if (threads.length === 0) {
      threadList.innerHTML = `
        <div class="fellowship-empty">
          <div class="fellowship-empty-icon">💬</div>
          <p>No discussions yet. Start the first one!</p>
        </div>
      `;
      return;
    }
    
    threadList.innerHTML = threads.map(t => `
      <div class="thread-item" data-id="${t.id}">
        <div class="thread-title">${t.title}</div>
        <div class="thread-meta">
          <span>By ${t.author_name}</span>
          <span>${t.reply_count} replies</span>
          <span>${formatDate(t.created_at)}</span>
        </div>
      </div>
    `).join("");
    
    threadList.querySelectorAll(".thread-item").forEach(el => {
      el.addEventListener("click", () => openThreadDetail(el.dataset.id));
    });
  } catch (err) {
    threadList.innerHTML = '<div class="fellowship-empty"><p>Failed to load discussions</p></div>';
  }
}

function formatDate(dateStr) {
  const d = new Date(dateStr);
  return d.toLocaleDateString();
}

// New Thread Modal
if (newThreadBtn) {
  newThreadBtn.addEventListener("click", () => {
    newThreadModal.classList.remove("hidden");
  });
}

if (closeNewThread) {
  closeNewThread.addEventListener("click", () => {
    newThreadModal.classList.add("hidden");
  });
}

if (newThreadForm) {
  newThreadForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const title = document.getElementById("threadTitle").value.trim();
    const body = document.getElementById("threadBody").value.trim();
    
    if (!title || !body) return;
    
    try {
      const res = await fetch("/api/fellowship/threads", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, body }),
      });
      
      if (res.ok) {
        newThreadModal.classList.add("hidden");
        document.getElementById("threadTitle").value = "";
        document.getElementById("threadBody").value = "";
        loadThreads();
      } else {
        const err = await res.json();
        alert(err.detail || "Failed to create discussion");
      }
    } catch (err) {
      alert("Failed to create discussion");
    }
  });
}

// Thread Detail Modal
async function openThreadDetail(threadId) {
  currentFellowshipThreadId = threadId;
  
  try {
    const res = await fetch(`/api/fellowship/threads/${threadId}`);
    const thread = await res.json();
    
    threadDetailBody.innerHTML = `
      <h3>${thread.title}</h3>
      <p class="thread-author">By ${thread.author_name} • ${formatDate(thread.created_at)}</p>
      <p>${thread.body}</p>
    `;
    
    repliesList.innerHTML = thread.replies.map(r => `
      <div class="reply-item">
        <div class="reply-author">${r.author_name} • ${formatDate(r.created_at)}</div>
        <div class="reply-text">${r.content}</div>
      </div>
    `).join("");
    
    if (thread.replies.length === 0) {
      repliesList.innerHTML = '<div class="fellowship-empty"><p>No replies yet. Be the first to respond!</p></div>';
    }
    
    fellowshipModal.classList.add("hidden");
    threadDetailModal.classList.remove("hidden");
  } catch (err) {
    console.error("Failed to load thread:", err);
  }
}

if (backToThreads) {
  backToThreads.addEventListener("click", () => {
    threadDetailModal.classList.add("hidden");
    fellowshipModal.classList.remove("hidden");
    loadThreads();
  });
}

if (closeThreadDetail) {
  closeThreadDetail.addEventListener("click", () => {
    threadDetailModal.classList.add("hidden");
    document.body.classList.remove("modal-open");
  });
}

if (replyForm) {
  replyForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const content = document.getElementById("replyText").value.trim();
    if (!content || !currentFellowshipThreadId) return;
    
    try {
      const res = await fetch(`/api/fellowship/threads/${currentFellowshipThreadId}/replies`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content }),
      });
      
      if (res.ok) {
        document.getElementById("replyText").value = "";
        openThreadDetail(currentFellowshipThreadId);
      } else {
        const err = await res.json();
        alert(err.detail || "Failed to post reply");
      }
    } catch (err) {
      alert("Failed to post reply");
    }
  });
}

// ============================================================
// VOICE INPUT FOR THRONE CHAT
// ============================================================

let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;

const voiceInputBtn = document.getElementById("voiceInputBtn");
const userInputEl = document.getElementById("userInput");

if (voiceInputBtn && userInputEl) {
  voiceInputBtn.addEventListener("mousedown", startVoiceRecording);
  voiceInputBtn.addEventListener("mouseup", stopVoiceRecording);
  voiceInputBtn.addEventListener("mouseleave", stopVoiceRecording);
  voiceInputBtn.addEventListener("touchstart", (e) => { e.preventDefault(); startVoiceRecording(); });
  voiceInputBtn.addEventListener("touchend", stopVoiceRecording);
}

async function startVoiceRecording() {
  if (isRecording) return;
  
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];
    
    mediaRecorder.ondataavailable = (e) => {
      audioChunks.push(e.data);
    };
    
    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
      stream.getTracks().forEach(track => track.stop());
      await transcribeAudio(audioBlob);
    };
    
    mediaRecorder.start();
    isRecording = true;
    voiceInputBtn.classList.add("recording");
  } catch (err) {
    console.error("Microphone access denied:", err);
    alert("Please allow microphone access to use voice input.");
  }
}

function stopVoiceRecording() {
  if (!isRecording || !mediaRecorder) return;
  
  mediaRecorder.stop();
  isRecording = false;
  voiceInputBtn.classList.remove("recording");
}

async function transcribeAudio(audioBlob) {
  try {
    userInputEl.value = "Transcribing...";
    userInputEl.disabled = true;
    
    const formData = new FormData();
    formData.append("audio", audioBlob, "recording.webm");
    
    const res = await fetch("/api/transcribe", {
      method: "POST",
      body: formData,
    });
    
    if (res.ok) {
      const data = await res.json();
      userInputEl.value = data.text || "";
      if (data.text) {
        userInputEl.focus();
      }
    } else {
      userInputEl.value = "";
      alert("Failed to transcribe audio. Please try again.");
    }
  } catch (err) {
    console.error("Transcription error:", err);
    userInputEl.value = "";
    alert("Transcription failed. Please try again.");
  } finally {
    userInputEl.disabled = false;
  }
}

// ============================================================
// VOICE INPUT FOR MASOWE CHAT
// ============================================================

let masoweMediaRecorder = null;
let masoweAudioChunks = [];
let masoweIsRecording = false;

const masoweVoiceBtn = document.getElementById("masoweVoiceBtn");
const masoweChatInput = document.getElementById("masoweChatInput");

if (masoweVoiceBtn && masoweChatInput) {
  masoweVoiceBtn.addEventListener("mousedown", startMasoweVoiceRecording);
  masoweVoiceBtn.addEventListener("mouseup", stopMasoweVoiceRecording);
  masoweVoiceBtn.addEventListener("mouseleave", stopMasoweVoiceRecording);
  masoweVoiceBtn.addEventListener("touchstart", (e) => { e.preventDefault(); startMasoweVoiceRecording(); });
  masoweVoiceBtn.addEventListener("touchend", stopMasoweVoiceRecording);
}

async function startMasoweVoiceRecording() {
  if (masoweIsRecording) return;
  
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    masoweMediaRecorder = new MediaRecorder(stream);
    masoweAudioChunks = [];
    
    masoweMediaRecorder.ondataavailable = (e) => {
      masoweAudioChunks.push(e.data);
    };
    
    masoweMediaRecorder.onstop = async () => {
      const audioBlob = new Blob(masoweAudioChunks, { type: "audio/webm" });
      stream.getTracks().forEach(track => track.stop());
      await transcribeMasoweAudio(audioBlob);
    };
    
    masoweMediaRecorder.start();
    masoweIsRecording = true;
    masoweVoiceBtn.classList.add("recording");
  } catch (err) {
    console.error("Microphone access denied:", err);
    alert("Please allow microphone access to use voice input.");
  }
}

function stopMasoweVoiceRecording() {
  if (!masoweIsRecording || !masoweMediaRecorder) return;
  
  masoweMediaRecorder.stop();
  masoweIsRecording = false;
  masoweVoiceBtn.classList.remove("recording");
}

async function transcribeMasoweAudio(audioBlob) {
  try {
    masoweChatInput.value = "Transcribing...";
    masoweChatInput.disabled = true;
    
    const formData = new FormData();
    formData.append("audio", audioBlob, "recording.webm");
    
    const res = await fetch("/api/transcribe", {
      method: "POST",
      body: formData,
    });
    
    if (res.ok) {
      const data = await res.json();
      masoweChatInput.value = data.text || "";
    } else {
      masoweChatInput.value = "";
      alert("Failed to transcribe audio. Please try again.");
    }
  } catch (err) {
    console.error("Transcription error:", err);
    masoweChatInput.value = "";
  } finally {
    masoweChatInput.disabled = false;
  }
}

// ============================================================
// LOGOUT CONFIRMATION
// ============================================================
const logoutBtn = document.getElementById("logoutBtn");
if (logoutBtn) {
  logoutBtn.addEventListener("click", (e) => {
    e.preventDefault();
    if (confirm("Are you sure you want to log out?")) {
      window.location.href = "/auth/logout";
    }
  });
}


// ============================================================
// SEND BUTTON CLICK HANDLER (MOBILE FIX)
// ============================================================
const masoweSendBtn = document.getElementById("masoweSendBtn");
if (masoweSendBtn) {
  masoweSendBtn.addEventListener("click", (e) => {
    const input = document.getElementById("masoweChatInput");
    const content = input ? input.value.trim() : "";
    
    console.log("Send button clicked, content:", content, "socket state:", masoweSocket?.readyState);
    
    if (!content) {
      console.log("No content to send");
      return;
    }
    
    if (!masoweSocket || masoweSocket.readyState !== WebSocket.OPEN) {
      console.log("WebSocket not connected, attempting reconnect...");
      connectMasoweChat();
      setTimeout(() => {
        if (masoweSocket && masoweSocket.readyState === WebSocket.OPEN) {
          masoweSocket.send(JSON.stringify({ type: "chat", content }));
          input.value = "";
        } else {
          alert("Chat not connected. Please try again.");
        }
      }, 1000);
      return;
    }
    
    masoweSocket.send(JSON.stringify({ type: "chat", content }));
    input.value = "";
  });
}

// ============================================================
// RUSHANGA ADMIN PANEL
// ============================================================

let allSubscribers = [];

function openRushangaModal() {
  if (rushangaModal) {
    rushangaModal.classList.remove("hidden");
    document.body.classList.add("modal-open");
    loadSubscribers();
  }
}

function closeRushangaModal() {
  if (rushangaModal) {
    rushangaModal.classList.add("hidden");
    document.body.classList.remove("modal-open");
  }
}

async function loadSubscribers() {
  if (!rushangaSubscribersList) return;
  
  rushangaSubscribersList.innerHTML = '<p class="rushanga-loading">Loading subscribers...</p>';
  
  try {
    const resp = await fetch("/api/admin/subscribers", { credentials: "include" });
    if (!resp.ok) throw new Error("Failed to load subscribers");
    
    const data = await resp.json();
    allSubscribers = data.subscribers || [];
    
    if (data.stats) {
      renderStats(data.stats);
    }
    
    renderSubscribers(allSubscribers);
  } catch (e) {
    console.error("Failed to load subscribers:", e);
    rushangaSubscribersList.innerHTML = '<p class="rushanga-loading" style="color:#ef4444;">Failed to load subscribers</p>';
  }
}

function renderStats(stats) {
  const statsEl = document.getElementById("rushangaStats");
  if (!statsEl) return;
  
  const statStyle = "flex:1;min-width:70px;background:rgba(212,175,55,0.1);border:1px solid rgba(212,175,55,0.3);border-radius:8px;padding:8px 10px;text-align:center;";
  const valueStyle = "font-size:1.3rem;font-weight:700;color:#d4af37;line-height:1.1;";
  const labelStyle = "font-size:0.65rem;color:#9ca3af;text-transform:uppercase;letter-spacing:0.03em;";
  
  statsEl.innerHTML = `
    <div class="rushanga-stat" style="${statStyle}">
      <div class="rushanga-stat-value" style="${valueStyle}">${stats.total || 0}</div>
      <div class="rushanga-stat-label" style="${labelStyle}">Total Users</div>
    </div>
    <div class="rushanga-stat" style="${statStyle}">
      <div class="rushanga-stat-value" style="${valueStyle}">${stats.new_today || 0}</div>
      <div class="rushanga-stat-label" style="${labelStyle}">New Today</div>
    </div>
    <div class="rushanga-stat" style="${statStyle}">
      <div class="rushanga-stat-value" style="${valueStyle}">${stats.active_paid || 0}</div>
      <div class="rushanga-stat-label" style="${labelStyle}">Paid Active</div>
    </div>
  `;
}

function renderSubscribers(subscribers) {
  if (!rushangaSubscribersList) return;
  
  if (subscribers.length === 0) {
    rushangaSubscribersList.innerHTML = '<p style="color:#9ca3af;text-align:center;padding:30px;">No subscribers found</p>';
    return;
  }
  
  const cardStyle = "display:flex;flex-direction:column;gap:10px;background:rgba(30,27,75,0.4);padding:12px;border-radius:8px;border:1px solid rgba(212,175,55,0.15);";
  const cardAdminStyle = "display:flex;flex-direction:column;gap:10px;background:rgba(212,175,55,0.1);padding:12px;border-radius:8px;border:1px solid rgba(212,175,55,0.5);";
  const cardSuspendedStyle = "display:flex;flex-direction:column;gap:10px;background:rgba(30,27,75,0.4);padding:12px;border-radius:8px;border:1px solid rgba(239,68,68,0.3);opacity:0.6;";
  const emailStyle = "color:#e5e7eb;font-weight:600;font-size:0.9rem;word-break:break-all;";
  const metaStyle = "display:flex;gap:10px;font-size:0.75rem;color:#9ca3af;flex-wrap:wrap;";
  const statusBaseStyle = "padding:3px 10px;border-radius:10px;font-size:0.7rem;font-weight:600;text-transform:uppercase;display:inline-block;";
  const actionsStyle = "display:flex;gap:8px;flex-wrap:wrap;";
  const suspendBtnStyle = "padding:6px 12px;border-radius:4px;font-size:0.75rem;font-weight:600;cursor:pointer;border:none;background:rgba(245,158,11,0.2);color:#f59e0b;";
  const unsuspendBtnStyle = "padding:6px 12px;border-radius:4px;font-size:0.75rem;font-weight:600;cursor:pointer;border:none;background:rgba(34,197,94,0.2);color:#22c55e;";
  const removeBtnStyle = "padding:6px 12px;border-radius:4px;font-size:0.75rem;font-weight:600;cursor:pointer;border:none;background:rgba(239,68,68,0.2);color:#ef4444;";
  
  rushangaSubscribersList.innerHTML = subscribers.map(sub => {
    const statusLabel = sub.is_admin ? "ADMIN" : sub.access_status.toUpperCase();
    let cardFinalStyle = cardStyle;
    if (sub.is_admin) cardFinalStyle = cardAdminStyle;
    else if (sub.is_suspended) cardFinalStyle = cardSuspendedStyle;
    
    let statusStyle = statusBaseStyle;
    if (sub.is_admin) statusStyle += "background:rgba(212,175,55,0.3);color:#d4af37;";
    else if (sub.access_status === "active") statusStyle += "background:rgba(34,197,94,0.2);color:#22c55e;";
    else if (sub.access_status === "expired") statusStyle += "background:rgba(245,158,11,0.2);color:#f59e0b;";
    else if (sub.access_status === "suspended") statusStyle += "background:rgba(239,68,68,0.2);color:#ef4444;";
    else statusStyle += "background:rgba(107,114,128,0.2);color:#9ca3af;";
    
    const expiresText = sub.access_expires_at 
      ? `Expires: ${new Date(sub.access_expires_at).toLocaleDateString()}`
      : sub.is_admin ? "Unlimited" : "";
    
    const actionsHtml = sub.is_admin ? '' : `
      <div style="${actionsStyle}">
        ${sub.is_suspended 
          ? `<button style="${unsuspendBtnStyle}" onclick="updateSubscriber('${sub.email}', 'unsuspend')">Unsuspend</button>`
          : `<button style="${suspendBtnStyle}" onclick="updateSubscriber('${sub.email}', 'suspend')">Suspend</button>`
        }
        <button style="${removeBtnStyle}" onclick="updateSubscriber('${sub.email}', 'remove')">Remove</button>
      </div>
    `;
    
    return `
      <div style="${cardFinalStyle}">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:10px;flex-wrap:wrap;">
          <div>
            <span style="${emailStyle}">${escapeHtml(sub.email || "No email")}</span>
            <div style="${metaStyle}">
              <span>Tier: ${sub.subscription_tier}</span>
              <span>Limit: ${sub.daily_limit}/day</span>
              ${expiresText ? `<span>${expiresText}</span>` : ""}
            </div>
          </div>
          <span style="${statusStyle}">${statusLabel}</span>
        </div>
        ${actionsHtml}
      </div>
    `;
  }).join("");
}

async function updateSubscriber(email, action) {
  if (!confirm(`Are you sure you want to ${action} ${email}?`)) return;
  
  try {
    const resp = await fetch("/api/admin/update-subscriber", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ email, action })
    });
    
    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.detail || "Failed to update subscriber");
    }
    
    const data = await resp.json();
    alert(data.message);
    loadSubscribers();
  } catch (e) {
    alert("Error: " + e.message);
  }
}

async function grantAccess() {
  const email = grantEmail ? grantEmail.value.trim() : "";
  const duration = grantDuration ? grantDuration.value : "1_month";
  const note = grantNote ? grantNote.value.trim() : "";
  
  if (!email) {
    showGrantResult("Please enter an email address", false);
    return;
  }
  
  if (!email.includes("@")) {
    showGrantResult("Please enter a valid email address", false);
    return;
  }
  
  try {
    const resp = await fetch("/api/admin/grant-access", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ email, duration, note })
    });
    
    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.detail || "Failed to grant access");
    }
    
    const data = await resp.json();
    showGrantResult(data.message, true);
    
    if (grantEmail) grantEmail.value = "";
    if (grantNote) grantNote.value = "";
    
    loadSubscribers();
  } catch (e) {
    showGrantResult("Error: " + e.message, false);
  }
}

function showGrantResult(message, success) {
  if (grantResult) {
    grantResult.textContent = message;
    grantResult.classList.remove("hidden", "success", "error");
    grantResult.classList.add(success ? "success" : "error");
    
    setTimeout(() => {
      grantResult.classList.add("hidden");
    }, 5000);
  }
}

// RUSHANGA event listeners
if (rushangaBtn) {
  rushangaBtn.addEventListener("click", openRushangaModal);
}

if (closeRushangaBtn) {
  closeRushangaBtn.addEventListener("click", closeRushangaModal);
}

if (rushangaModal) {
  rushangaModal.addEventListener("click", (e) => {
    if (e.target === rushangaModal) {
      closeRushangaModal();
    }
  });
}

if (rushangaRefreshBtn) {
  rushangaRefreshBtn.addEventListener("click", loadSubscribers);
}

if (grantAccessBtn) {
  grantAccessBtn.addEventListener("click", grantAccess);
}

// Search filtering
if (rushangaSearchInput) {
  rushangaSearchInput.addEventListener("input", (e) => {
    const query = e.target.value.toLowerCase().trim();
    if (!query) {
      renderSubscribers(allSubscribers);
    } else {
      const filtered = allSubscribers.filter(sub => 
        (sub.email || "").toLowerCase().includes(query) ||
        (sub.first_name || "").toLowerCase().includes(query) ||
        (sub.last_name || "").toLowerCase().includes(query)
      );
      renderSubscribers(filtered);
    }
  });
}

// Tab switching
document.querySelectorAll(".rushanga-tab").forEach(tab => {
  tab.addEventListener("click", () => {
    const tabName = tab.dataset.tab;
    
    document.querySelectorAll(".rushanga-tab").forEach(t => t.classList.remove("active"));
    document.querySelectorAll(".rushanga-tab-content").forEach(c => c.classList.add("hidden"));
    
    tab.classList.add("active");
    
    if (tabName === "subscribers") {
      document.getElementById("rushangaSubscribersTab")?.classList.remove("hidden");
    } else if (tabName === "grant") {
      document.getElementById("rushangaGrantTab")?.classList.remove("hidden");
    }
  });
});
