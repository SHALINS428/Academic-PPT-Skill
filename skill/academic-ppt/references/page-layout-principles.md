# Page Layout Principles

## Goal

This file translates professional slide-design guidance into page-level rules for thesis defense decks.

It is meant to be operational, not inspirational:
- the planner should reduce density before the generator lays out the page
- the generator should preserve visual hierarchy and whitespace
- page recipes should change by slide purpose instead of reusing one generic content box

## External Guidance Distilled

This layout system is aligned with guidance repeatedly emphasized in academic and science-presentation references:
- strong message titles instead of empty labels
- one main idea per slide
- fewer bullets and more visual evidence
- enough whitespace to separate hierarchy
- redraw or simplify paper figures for slide readability
- keep repeated branding minimal so it does not compete with the argument

Useful references:
- Harvard Catalyst, `Slides`: message-driven titles, visual-first scientific slides, less bullet dependence
- MIT Comm Lab, `Redesigning Existing Figures for Slides`: figures should be simplified, cropped, or rebuilt for talk delivery
- Queen's University, `Effective Visuals`: one clear idea, visible hierarchy, readable visuals
- PLOS Computational Biology, `Ten Simple Rules for Better Slides`: reduce cognitive load, emphasize signal over density

Reference links:
- https://catalyst.harvard.edu/writing-communication-center/visualize-science/slides/
- https://mitcommlab.mit.edu/cee/2024/01/15/redesigning-existing-figures-for-slides/
- https://www.queensu.ca/ctl/resources/instructors/instructional-strategies/interactive-lecturing/effective-visuals
- https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1009554

## Global Layout Contract

For 16:9 defense decks:
- reserve the top 14% to 18% of the slide for navigation, page theme, and headline hierarchy
- keep the main claim in the top-left reading path
- keep one dominant visual or evidence block per slide
- prefer 2 to 3 evidence bullets on content pages
- each bullet should usually fit in one to two short lines
- avoid stacking more than three cards with equal visual weight
- use alignment, spacing, and scale before using more color

## Typography Budget

Recommended default sizes for content slides:
- page theme label: about `13.5pt`
- page theme sentence: about `13.5pt`
- eyebrow / section cue: about `13.5pt`
- main claim headline: about `18pt` to `22pt`
- secondary explanatory sentence: about `13.5pt` to `15pt`
- body bullets: about `13.5pt` to `14.5pt`
- chart or image caption: about `13.5pt`

The design goal is not large text everywhere.
The design goal is clear contrast between levels.

## Minimum Font Floor

For this skill, visible editable text should not go below:
- `18px`

Operational conversion:
- treat `18px` as roughly `13.5pt`

Implication:
- if a layout needs smaller text to fit, the layout is too dense
- reduce copy, remove low-value labels, or split the slide instead

## Density Budget

Default density limits:
- content pages: maximum `3` evidence bullets
- innovation pages: maximum `3` innovation claims
- limitations pages: split into `2 + 2` when possible
- agenda pages: `4` to `6` items
- chapter divider pages: no extra bullets

If a slide needs more than these limits:
- split it into two slides
- convert part of the text into a figure
- move detail into speaker notes instead of the visible page

## Visual Weight Rules

Use visual area intentionally:
- narrative / statement pages: text block `45%` to `55%`, support panel `25%` to `35%`
- method pages: visual block should usually take `50%` to `60%` of the width
- results pages: chart or figure should usually take at least `40%` of the visible information weight
- innovation pages: use three clearly separated columns, not one long paragraph
- limitations pages: two balanced columns with different accents for `current boundary` and `future work`

Do not let the shell background become the dominant visual.
The argument and evidence should stay dominant.

## Page-Type Rules

### Cover

- keep the thesis title dominant
- keep metadata to one compact block
- school branding may appear in the top-right badge only
- do not add extra decorative lines, seals, or repeated campus graphics

### Agenda

- keep the list short and scan-friendly
- make each item parallel in wording
- do not place dense descriptions under every agenda item

### Chapter Divider

- use one big chapter title and one short descriptor
- do not add the content-page theme module here
- divider pages should reset rhythm, not compete with content pages

### Background / Problem

- use a statement-first layout
- one judgment sentence at the top
- 2 to 3 supporting points below
- only add a figure if it truly clarifies the scenario or gap

### Technical Route / Method

- prefer left-text right-visual or top-claim bottom-process structure
- the visual should carry the pipeline, architecture, or module relation
- text should explain the design choice, not repeat the figure labels

### Student Work / Implementation

- highlight what the student actually implemented
- use screenshots only when they prove workflow, interface, or deployment evidence
- if using screenshots, pair them with a concise reading cue, not with dense narration

### Experiment / Results

- top band for 2 to 3 metrics or conclusion cues
- bottom-left for interpretation
- bottom-right for chart or result image
- charts must show what is compared, what changes, and what conclusion follows

### Innovation

- use three separated innovation cards or columns at most
- each claim should map to a method change and an evidence source
- avoid summary paragraphs here

### Limitations / Future Work

- separate current boundary and next-step direction visually
- do not hide limitations in small text
- keep the tone calm and credible

## Branding Rule

For school defense decks, the default should remain:
- `subtle_badge`

Meaning:
- one small badge in the top-right area
- optional logo plus school wordmark
- no repeated campus motifs in body pages
- branding should be visually weaker than both the slide title and the evidence

## Generator Implications

The generator should enforce:
- shorter bullets
- fewer bullets
- stronger claim headlines
- figure-first method and result pages
- cleaner top theme module on content pages only

The planner should enforce:
- shorter takeaways
- denser text cut before layout
- page-type-specific design hints
- figure matching before fallback diagram generation
