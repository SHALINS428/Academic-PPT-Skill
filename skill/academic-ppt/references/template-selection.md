# Template Selection

## Default Recommendation

Default to:
- `academic_premium`

This is now the preferred thesis-defense baseline because it is visibly more refined than the older plain academic shell while still staying readable and committee-friendly.
Its current composition is:
- `exhibit` for cover/chapter/ending
- `mckinsey` for agenda structure
- `google_style` for lower-noise content pages

## Design Recipes

Use `deck_identity.visual_direction` to select one of these recipes:

- `academic_premium`
- `academic_precision`
- `medical_precision`
- `executive_premium`
- `product_modern`
- `editorial_premium`
- `ai_modern`
- `campus_academic`
- `campus_medical`

## Recipe Guidance

### `academic_premium`

Use for:
- most thesis defense decks
- engineering and computer science defense decks
- users who want the deck to look noticeably more premium without becoming too business-like

### `academic_precision`

Use for:
- conservative academic settings
- when the user wants a safer and more traditional university-defense appearance

### `medical_precision`

Use for:
- medical and biomedical research decks
- hospital-facing academic presentations

### `executive_premium`

Use for:
- users who explicitly want consulting-grade structure
- decks that should feel concise, strategic, and boardroom-clean

### `product_modern`

Use for:
- technical product presentations
- software systems and project showcase decks
- users who want a brighter and more tech-company-like appearance

### `editorial_premium`

Use for:
- users who want stronger artistic polish
- premium dark openings and chapter pages
- a more exhibition-like and conclusion-first tone

### `ai_modern`

Use for:
- model, agent, LLM, and AI-system presentations
- users who want a more contemporary tech-talk style

### `campus_academic`

Use for:
- school defense decks that still need premium design
- cases where school identity should exist, but only as a subtle top-right badge

### `campus_medical`

Use for:
- hospital or medical-school decks with subtle institutional branding

## School Branding Rule

For school-specific defense decks, the default branding rule is:
- keep the chosen design recipe
- add only a small school badge and wordmark in the top-right corner
- avoid repeating school motifs across the rest of the page

This is controlled by:
- `deck_identity.branding_mode = "subtle_badge"`

Only use:
- `deck_identity.branding_mode = "full_template"`

when the user explicitly wants the old full-campus shell such as `重庆大学`.

## Legacy Compatibility

Legacy raw shell names are still supported:
- `academic_defense`
- `medical_university`
- `mckinsey`
- `google_style`
- `exhibit`
- `anthropic`
- `重庆大学`

But they are internally mapped into the new recipe system where appropriate.

## Page-Type Strategy

The upgraded generator separates:
- shell background choice
- content layout treatment
- school branding mode

That separation is what makes the deck less cluttered and more reusable.

Recommended behavior:
- cover, toc, chapter, ending: use borrowed SVG shells
- content pages: use the borrowed shell plus editable PowerPoint-native overlays
- school mode: keep the shell clean and use only the top-right badge
- page interiors: choose a page-type variant instead of reusing one card layout for all content pages
- layout guardrails from `references/page-layout-principles.md` should override any template tendency toward clutter
- selective `guizang-ppt-skill` borrowing should mainly affect body-page grid discipline and opening-page rhythm, not push the deck toward web-demo styling

## Further Reading

For the full breakdown of what was borrowed from each `ppt-master` template, read:
- `references/design-language-catalog.md`
- `references/page-layout-principles.md`
- `references/guizang-academic-adaptation.md`
