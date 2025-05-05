# 🌐 Concierge Web App (Frontend)

Built with Astro. Enables multilingual chat interface with escalation to WhatsApp.

---

## 🧭 Features

- Chat interface auto-translates using OpenAI
- Triggers WhatsApp callbacks on request
- Mobile-optimized

---

## 🛠 Development

```bash
npm install
npm run dev
.env must provide:

API_URL for backend

WhatsApp API keys (via Messenger)

📁 Structure
src/pages/index.astro — Chat UI

Connects to /respond and /callback on backend