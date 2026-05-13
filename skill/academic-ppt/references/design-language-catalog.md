# Design Language Catalog

## Goal

This skill should no longer behave like a single fixed academic template.

It now treats the borrowed `ppt-master` layouts as a design library and maps them into reusable design recipes that can be called by the planner or set directly in `deck_identity.visual_direction`.

## Core Design Recipes

### `academic_premium`

Default recommendation for thesis defense decks when visual polish matters.

Borrowed DNA:
- `exhibit` for cover, chapter, and ending
- `mckinsey` for agenda structure
- `google_style` for cleaner content-page shell

Traits:
- dark premium opening and section divider
- clean white content slides with lower visual noise
- restrained consulting-style whitespace
- suitable for research defense, engineering defense, and committee-facing presentations

### `academic_precision`

Conservative academic route.

Borrowed DNA:
- `academic_defense`

Traits:
- formal
- restrained
- high readability
- lower design risk, lower visual surprise

### `medical_precision`

Medical and biomedical academic route.

Borrowed DNA:
- `medical_university`

Traits:
- protocol-like structure
- blue/green evidence feel
- suitable for medical research or hospital-facing presentations

### `executive_premium`

Highest consulting flavor.

Borrowed DNA:
- `mckinsey`

Traits:
- conclusion-first
- strict structure
- light theme, premium whitespace
- strong when the user wants “boardroom quality” rather than “campus template”

### `product_modern`

Tech-company clean style.

Borrowed DNA:
- `google_style`

Traits:
- brighter
- more rounded
- cleaner KPI and dashboard feel
- suitable for technical sharing, project showcase, and software-defense decks

### `editorial_premium`

Dark premium editorial style.

Borrowed DNA:
- `exhibit`

Traits:
- strongest premium feel
- dark opening and darker narrative tone
- strong for conclusion-first storytelling

### `ai_modern`

Modern AI / LLM talk route.

Borrowed DNA:
- `anthropic` for cover, toc, chapter, ending
- `google_style` for content shell to avoid over-structured card placeholders

Traits:
- more contemporary
- useful for model/system/agent presentations
- works when the user wants a less traditional academic look

## Branding Rule

School branding should be decoupled from the page shell.

Default school branding mode:
- `subtle_badge`

Meaning:
- only a small badge in the top-right corner
- optional logo plus school wordmark
- no repeated school graphics elsewhere
- no full-page campus branding unless the user explicitly asks for it
- badge size should stay visually secondary to the slide title and content

## Branding Modes

### `none`

No institution badge.

### `subtle_badge`

Recommended default for school defense decks.

Behavior:
- keep the chosen design recipe
- add only the school badge and wordmark in the top-right corner
- preserve the premium layout instead of switching to a heavy school template

### `full_template`

Use only when the user explicitly wants the original campus template.

Behavior:
- allows a fully branded shell such as `重庆大学`
- should be exceptional, not the default

## What Each Borrowed Template Contributes

### From `mckinsey`

Borrow:
- whitespace discipline
- header hierarchy
- cleaner agenda and content shells
- low-noise business-grade refinement

Do not over-borrow:
- overly business phrasing
- generic consulting jargon

### From `google_style`

Borrow:
- rounded light cards
- crisp KPI presentation
- lighter technology-forward polish
- cleaner product-report feel
- cleaner content-page shell without heavy institutional framing

Do not over-borrow:
- too many brand-color accents on one page

### From `exhibit`

Borrow:
- premium dark covers
- chapter divider dignity
- gold accent restraint
- conclusion-first seriousness

Do not over-borrow:
- too much dark content area
- excessive “confidential” business tone in academic decks

### From `anthropic`

Borrow:
- modern AI talk atmosphere
- cleaner page-label behavior
- contemporary technical narrative feel

Do not over-borrow:
- fixed three-card shell for all content pages

### From `guizang-ppt-skill`

Borrow selectively:
- finite page-layout vocabulary instead of ad hoc slide composition
- stronger grid lock for technical evidence pages
- editorial weight concentrated on opening and divider pages
- cleaner hierarchy with a kicker above the main message
- remove micro-labels when they hurt readability

Do not over-borrow:
- web-native presentation assumptions
- decorative small text
- art-direction experiments that weaken method or result readability

### From `academic_defense`

Borrow:
- academic safety
- clarity
- defense friendliness

Do not over-borrow:
- plainness
- repetitive blue box structure

## Practical Rule

When the user says:
- “学校答辩但不要太土” -> prefer `academic_premium` + `subtle_badge`
- “更像咨询公司/战略汇报” -> prefer `executive_premium`
- “更像科技公司/产品发布” -> prefer `product_modern`
- “更高级、更有艺术感、更像展陈” -> prefer `editorial_premium`
- “AI / agent / 模型方向汇报” -> prefer `ai_modern`

## Generator Rule

The skill should always separate:
- `design recipe`
- `school branding mode`
- `content page layout`

The content page layout must also obey:
- message-first hierarchy
- reduced bullet density
- strong whitespace
- visual-first method and results pages

It should also allow page-level layout hints such as:
- `statement_spread`
- `statement_sidebar`
- `method_architecture_split`
- `method_process_band`
- `results_metric_band`
- `innovation_triptych`
- `boundary_dual_column`

That separation is what prevents the deck from collapsing back into a single rigid academic template.
