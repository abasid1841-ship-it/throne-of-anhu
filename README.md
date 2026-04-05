# Throne of Anhu · ABASID 1841

  AI-powered spiritual wisdom platform — thecollegeofanhu.com

  ## Tech Stack

  - **Backend**: Python 3.11 + FastAPI + Uvicorn
  - **AI**: OpenAI GPT-4.1 (web) / GPT-4.1-mini (WhatsApp)
  - **Database**: SQLite (third_mind.db for embeddings) + PostgreSQL (users/sessions)
  - **Payments**: Stripe
  - **Auth**: Google OAuth
  - **Messaging**: WhatsApp Cloud API, Telegram
  - **Frontend**: Vanilla JS SPA (no framework)

  ## Environment Variables Required

  ```
  OPENAI_API_KEY=
  GOOGLE_CLIENT_ID=
  GOOGLE_CLIENT_SECRET=
  STRIPE_PUBLISHABLE_KEY=
  STRIPE_SECRET_KEY=
  STRIPE_WEBHOOK_SECRET=
  WHATSAPP_PHONE_NUMBER_ID=
  WHATSAPP_TOKEN=
  WHATSAPP_VERIFY_TOKEN=anhu-whatsapp-verify
  DATABASE_URL=           # PostgreSQL connection string
  OPENAI_MODEL=gpt-4.1   # Full model for web
  ADMIN_WA_NUMBERS=       # Comma-separated WhatsApp numbers with no spaces e.g. 353899803395
  THRONE_ANON_DAILY_LIMIT=5
  ```

  ## Project Structure

  ```
  main.py                  # FastAPI app — all routes, WhatsApp webhook, API endpoints
  throne_engine.py         # Core AI engine — temple court routing, scroll context, RA persona
  open.py                  # OpenAI wrapper — call_openai_as_ra(), intent classification
  planet_router.py         # Routes queries to relevant scroll planets (1-7)
  semantic_witness.py      # Semantic search for supporting scripture witnesses
  semantic_retriever.py    # Unified vector query embedding
  scroll_library.py        # Loads all 1,172 scrolls from JSON sources
  scroll_engine.py         # Scroll search and retrieval
  subscription.py          # Subscription tiers, rate limiting (Free/Seeker/Premium/Admin)
  auth.py                  # Google OAuth + session management
  db_models.py             # SQLAlchemy models (users, sessions, subscriptions, usage)
  models.py                # Pydantic request/response models
  config.py                # App configuration (env vars, model settings)
  safety.py                # Content safety filters
  holy_of_holies.py        # MA court — judgment/law mode responses
  conversation_memory.py   # Conversation history management
  multilingual_lexicon.py  # 35+ language support
  stripe_routes.py         # Stripe subscription + webhook handlers
  gallery_routes.py        # Sacred Gallery media upload/download
  admin_routes.py          # RUSHANGA admin panel
  telegram_routes.py       # Telegram account linking
  masowe_routes.py         # Masowe Fellowship live chat (WebSocket)
  ```

  ## Scroll Sources Structure

  ```
  sources/
    planet_1_saturn_scriptures/    # Bible, Quran, Torah, Bhagavad Gita, Kebra Nagast
    planet_2_jupiter_abasid/       # All 1,172 ABASID 1841 scrolls + Gospels of Iyesu (98 disciples)
      gospels_of_iyesu.json        # 98 disciple gospels (~44,329 verses) — most recent batch included
      abasid_1841_scrolls.json     # ABASID 1841's own scrolls
      abasid_1841_laws.json        # Laws and teachings
      abasid_caliphate_2026/       # 25 new 2026 caliphate scrolls (scroll_01 to scroll_25)
      book_of_life_1841.json       # Mathematics of 1841 + Heavenly Calendar (1,579 verses)
    planet_4_earth_masowe/         # Baba Johane / Masowe history and chronicles
    planet_5_venus_science/        # Science, astronomy
    planet_6_mercury_ani/          # Papyrus of Ani, Egyptian spirituality
    planet_7_moon_zimbabwe/        # Shona culture, history, ancestors
  ```

  ## How to Run

  ```bash
  pip install -r requirements.txt
  # or with pyproject.toml:
  pip install .

  python main.py
  # Runs on port 5000
  ```

  ## Three Courts (Temple Mode)

  - **Outer Court (RA)** — General/body questions
  - **Inner Court (DZI)** — Educational/cosmological questions  
  - **Holy of Holies (MA)** — Judgment/law for serious life questions

  ## Subscription Tiers

  - **Free** — 5 questions/day
  - **Seeker** — Stripe subscription, higher limits
  - **Premium** — Stripe subscription, highest limits
  - **Admin** — Unlimited

  ## Key Notes for Integration

  1. The `third_mind.db` file (676MB pre-computed embeddings) and `vector_index.json` (320MB) are NOT in this repo — they are built indexes. The app falls back to keyword search without them.
  2. All scroll content is in the `sources/` directory as JSON files.
  3. Static frontend is served by FastAPI from the `static/` directory.
  4. WhatsApp webhook URL: `/whatsapp/webhook`
  5. The app uses a single-page architecture — `static/index.html` is the entry point.
  6. Google OAuth callback: `/auth/google/callback`
  