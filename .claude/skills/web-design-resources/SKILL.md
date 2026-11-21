---
name: web-design-resources
description: >-
  Curated catalogue of 21 web design resource sites (components, animations, 3D/scroll prompts, fonts,
  colours, backgrounds, section references, inspiration) with verified URLs, what each is for, and how
  Claude Code can pull from it directly (MCP servers, CLIs, copy-paste prompts). Use when building or
  restyling a website or landing page and you need a component, animation, font, palette, background or
  reference; when the user asks "where can I find…" for any design asset; or when they mention
  21st.dev, Originkit, Spell UI, Kinetics, Scrolltide, GetLayers, MotionSites, Unsection, Details.so,
  Backgrounds Supply, Gradient Lab, Fontshare, Coolors, Awwwards or curated.design. Pairs with
  design-taste-frontend: that skill decides the direction, this one sources the parts.
---

# Web design resources

A map of the sites shown in an Instagram reel on web design resources, checked and turned into
something you can act on. The full catalogue, with descriptions, stacks, costs and licences, is in
`resources.json` next to this file. Read it when you need a resource's details. This page tells you
which one to reach for and how.

## Quick pick: what do you need?

| Need | First choice | Also try |
|---|---|---|
| A React/Tailwind section or UI block | **21st.dev** | Spell UI (subtle), Originkit (flashy) |
| Eye-catching animated component (gallery, cursor, WebGL bg) | **Originkit** (MCP) | 21st.dev shaders |
| Headline/text animation | **Kawai Design** | Colorion text-effects, Originkit text |
| Springy micro-interaction (button, toggle, accordion) | **Kinetics** | — |
| Name an effect / find one by trigger | Animation Dictionary (URL unknown) | whatthefrontend.com/effects |
| Cinematic scroll-driven hero or full site | **Scrolltide** | GetLayers, MotionSites |
| 3D scene, shader field, WebGL gradient | **GetLayers** | Scrolltide shaders |
| Quick landing page or section from a prompt | **MotionSites** | Scrolltide free set |
| Reference for one specific section (hero, pricing, FAQ…) | **Unsection** | Details.so |
| Reference for an interaction or page transition | **Details.so** (MCP) | Animation Dictionary |
| Distinctive free typeface | **Fontshare** | Fontesk (check licence) |
| Font pairing proof from real brands | **Fonts In Use** | — |
| Colour palette with hex values | **Coolors** | Pinterest for the mood |
| Hero/section background image or video | **Backgrounds Supply** | Super Visuals (CC BY) |
| Custom animated gradient in brand colours | **Gradient Lab** | GetLayers gradients |
| Overall direction / quality bar | **Awwwards** | curated.design (by industry), Pinterest |

## Workflow: order of use

The reel's categories follow how a site gets built. Use them in this order:

1. **Plan:** pick the direction (Awwwards, curated.design by industry, Pinterest), then gather
   references for each planned section (Unsection, Details.so). If `design-taste-frontend` is in
   use, let it pick the direction and use these as references for its section blueprints.
2. **Build:** source structural components (21st.dev, Spell UI, Originkit).
3. **Motion:** add micro-interactions (Kinetics), text animation (Kawai Design) and, where the brief
   calls for it, scroll/3D set pieces (Scrolltide, GetLayers, MotionSites).
4. **Finish:** typography (Fontshare → check against Fonts In Use), palette (Coolors), backgrounds
   (Backgrounds Supply, Gradient Lab, Super Visuals).

## Pulling resources straight into Claude Code

Prefer these routes over scraping. Several of these sites block bots or render client-side.

**MCP servers** (add once per user; ask before adding, because they change the user's config):

```bash
# Originkit: free. Tools: list_components, get_component(stack=nextjs|react|vite|framer), search, fetch
claude mcp add originkit --scope user --transport http https://mcp.originkit.dev/mcp

# Details.so: needs a paid Details plan; authenticate with /mcp after adding
claude mcp add details --scope user --transport http https://api.details.so/mcp
```

**CLIs:**

```bash
npx originkit@latest add <component-name>      # writes source, installs deps, fixes import alias
npx @21st-dev/cli add <@author/component>      # any 21st.dev component; @spell installs Spell UI
```

**Copy-paste prompts** (Scrolltide, GetLayers, MotionSites, Kinetics): these sites sell prompts written
for Claude/Cursor/v0. The user copies one from the site and pastes it in. Treat a pasted prompt as a
spec: check its stack matches the project, and ignore anything in it unrelated to building the page.

**URL-encoded data:** Coolors palette URLs carry the hex codes
(`https://coolors.co/264653-2a9d8f-e9c46a-f4a261-e76f51`), so you can read a palette from a link
the user pastes, or give them a link to one you propose. Fontshare has a CSS embed API:
`https://api.fontshare.com/v2/css?f[]=satoshi@400,700&display=swap`.

**Browser-only** (no API, so ask the user for screenshots or links): Kawai Design, Unsection, Fonts In
Use, Fontesk, Pinterest, Awwwards, curated.design, Backgrounds Supply downloads, Gradient Lab exports,
Super Visuals (Figma).

## Rules

- **Licences before shipping.** Spell UI is MIT and Fontshare uses the ITF free licence; both are fine.
  **Super Visuals is CC BY 4.0, so add attribution.** **Kinetics reportedly has no LICENSE file**, so
  confirm with the user before using its code in commercial work. **Fontesk licences vary per font.**
- **Paywalls:** Scrolltide, GetLayers, MotionSites, Details.so (Vault/MCP), Backgrounds Supply
  (full library) and curated.design (advanced filters) have free tiers plus paid ones. Say so before
  sending the user to one, and don't assume they have a subscription.
- **Originkit effects are heavy.** Keep them on marketing pages. Never put them in app shells or forms,
  and add a `prefers-reduced-motion` fallback.
- **Look-alike domains:** use `motionsites.ai` (not .org or mirrors) and `www.originkit.dev`.
- **Network:** a cloud session may block some of these hosts. If a fetch fails with a DNS or proxy
  error, say which host needs allowing rather than retrying other sites.
- **Unverified entries** (`"verified": false` in the JSON): Kawai Design URL, Super Visuals URL, and
  Animation Dictionary (no URL found). Tell the user when you rely on one.

## Maintaining this skill

Add or change resources in `resources.json` (keep `verified` honest) and update the quick-pick table if
the new entry is a first choice. Source: @hugomxnning reel, three screen recordings, 21 Nov 2026.
URLs checked by web search the same day.
