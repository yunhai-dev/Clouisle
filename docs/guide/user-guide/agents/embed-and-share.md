# Agent Embed & Independent Run View

This guide explains how to share published AI agents via the dedicated Run page and embed them into external websites as interactive chat widgets.

---

## Overview

Once an agent is configured and published, Clouisle provides two distinct delivery channels:

1. **Independent Run Page (`/run/{agent_id}`)**: A distraction-free, full-screen conversational interface designed for team members and authenticated users.
2. **Embeddable Chat Widget (`/embed/agents/{agent_id}/...`)**: A secure integration for embedding agents into SaaS apps, documentation portals, or corporate landing pages using a scoped API key (`clou_...`).

---

## 1. Independent Run Page (`/run/{agent_id}`)

The Run view provides a clean, standalone interface tailored for dedicated task execution without the clutter of the studio sidebar or settings drawers.

```
┌────────────────────────────────────────────────────────────────────────┐
│ 🤖 Financial Analyst Agent                           [Team: Finance]   │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  🤖 Financial Analyst                                                  │
│  Upload quarterly earnings reports or ask financial modeling questions │
│                                                                        │
│  [Analyze Q3 Revenue]  [Model Cashflow]  [Compare Competitors]         │
│                                                                        │
│  👤 User: Analyze the uploaded Q3 report.                              │
│                                                                        │
│  🤖 Financial Analyst:                                                 │
│  💭 Thought for 2.4s (Reading file: Q3_Financials.pdf)...              │
│  Here is the summary of Q3 financial performance...                    │
│                                                                        │
├────────────────────────────────────────────────────────────────────────┤
│  [📎] Ask a question or drop a spreadsheet...                   [Send] │
└────────────────────────────────────────────────────────────────────────┘
```

### Accessing the Run Page
- From the **Apps** page (`/app/apps`), hover over any published agent card and click **Run**.
- Or navigate directly to `https://<your-clouisle-domain>/run/{agent_id}`.

### Features
- **Distraction-free Canvas**: Optimized for deep interaction, document analysis, and iterative multi-turn conversations.
- **Dynamic Variable Prompting**: If the agent contains required variables (e.g., `client_id`, `locale`), the run page presents a clean input banner before starting.
- **Full Capabilities**: Complete support for attachments, image lightbox, document previews, `ask_user` interaction forms, and multi-version message branching.

---

## 2. Embeddable Chat Widget

Clouisle allows you to embed published agents into third-party web pages via either a **Floating Chat Bubble** or an **Inline Iframe**.

### Enabling Embedding

1. Open your agent in the **Agent Studio** (`/app/apps/{agent_id}`).
2. Ensure the agent is **Published**.
3. Click the **Embed** button on the top toolbar to open the `EmbedConfigurationDrawer`.
4. Toggle **Enable Embedding** on.
5. Generate or select a team API key (`clou_...`) with agent chat permissions.

### Configuration Options

| Option | Description | Example |
|---|---|---|
| **Allowed Domains** | Restrict widget loading to specific browser origins (`Origin` / `Referer` check for browser clients) | `https://example.com, https://app.example.com` |
| **Widget Mode** | Choose between a floating launcher bubble or an inline embed | `Floating Bubble` or `Inline Iframe` |
| **Theme & Accent Color** | Customize the widget primary color to match your brand | `#2563eb` (Blue) or dark/light auto-match |
| **Chat Bubble Position** | Screen placement for the floating trigger button | `Bottom Right` or `Bottom Left` |
| **Default Open** | Automatically expand the chat window upon page load | `true` / `false` |

---

## 3. Integration Code Examples

### Option A: Floating Web Component (Script Tag)

Paste this snippet immediately before the closing `</body>` tag on your website:

```html
<!-- Clouisle Agent Chat Widget -->
<script
  src="https://<your-clouisle-domain>/embed/clouisle-chat.js"
  data-agent-id="550e8400-e29b-41d4-a716-446655440000"
  data-api-key="clou_a1b2c3d4e5f6..."
  data-theme="auto"
  data-position="bottom-right"
  async
></script>
```

### Option B: Inline Iframe Embedding

To embed the agent conversation directly inside a container on your page:

```html
<iframe
  src="https://<your-clouisle-domain>/embed/agent/550e8400-e29b-41d4-a716-446655440000?token=clou_a1b2c3d4e5f6...&theme=light"
  width="100%"
  height="700px"
  frameborder="0"
  allow="microphone; camera; clipboard-write"
  style="border-radius: 12px; border: 1px solid #e5e7eb;"
></iframe>
```

---

## 4. Security & Access Control

- **API Key Authentication**: Embedded widgets authenticate using a team API key (`clou_...`) passed in the `token` query parameter or `Authorization: Bearer <key>` header.
- **Domain Verification**: When configured, `allowed_domains` restricts where browser clients can load the widget by verifying the `Origin` and `Referer` headers. (Note: API key authentication remains the primary access control).
- **Rate Limiting**: Embedded chats inherit platform rate limits to protect backend LLM quotas and infrastructure.
- **Isolated Scope**: Embedded sessions cannot access internal team models, settings, or administrative management endpoints.
