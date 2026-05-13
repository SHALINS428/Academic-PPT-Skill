# Guizang Academic Adaptation

Source repository:
- https://github.com/op7418/guizang-ppt-skill

## Purpose

This note explains what should be borrowed from `guizang-ppt-skill` for thesis defense decks and what should not.

The original project is broader than academic defense.
It includes stronger editorial, web-presentation, and art-direction ideas.
For thesis PPT, those ideas must be filtered through academic readability and defense-room constraints.

## What Is Worth Borrowing

### 1. Layout Lock Instead Of Freeform Improvisation

Useful idea:
- build from a limited set of named page layouts
- make each layout correspond to a communication goal

Academic adaptation:
- background/problem -> statement-first layout
- method/architecture -> text plus structure split
- results -> metric band plus chart area
- innovation -> three-claim layout
- limitations -> dual-column layout

Why it matters:
- prevents every content page from collapsing into the same generic card template
- improves rhythm across the deck

### 2. Swiss-Style Discipline For Evidence Pages

Useful idea:
- strict alignment
- stable left edge
- stronger whitespace
- restrained color use

Academic adaptation:
- use this discipline mainly for method, experiment, and result pages
- let the argument and evidence stay dominant

Why it matters:
- technical defense pages benefit more from clarity than from visual tricks

### 3. Editorial Weight Only Where It Helps

Useful idea:
- cover and chapter pages can carry more mood and visual theater

Academic adaptation:
- allow more premium editorial feeling on cover, chapter divider, and ending pages
- keep body pages cleaner and lighter

Why it matters:
- preserves premium feel without reducing committee readability

### 4. Kicker Above Title, Not Decorative Noise Around Title

Useful idea:
- small section cue above the main title
- message hierarchy is read top-down

Academic adaptation:
- use a restrained top theme or eyebrow label
- do not let this label compete with the main takeaway

Why it matters:
- works well for thesis sections and improves page scanability

### 5. Image Slot Planning

Useful idea:
- visuals should be planned into fixed slots rather than inserted loosely at the end

Academic adaptation:
- method pages should expect a workflow or architecture visual
- system pages should expect a screenshot or structure diagram
- result pages should expect a chart or result figure

Why it matters:
- makes the generator less brittle when real thesis figures are available

### 6. Checklist-Driven Validation

Useful idea:
- design quality should be checked against explicit criteria instead of taste alone

Academic adaptation:
- use readable font floor
- cap bullet density
- keep one main claim per slide
- require figure purpose and result interpretation

Why it matters:
- improves reproducibility across different theses

## What Should Not Be Borrowed Blindly

### 1. Web-Presentation Mechanics

Do not borrow as a default:
- swipe-native logic
- browser-specific interaction assumptions
- motion-heavy storytelling patterns

Reason:
- a thesis defense deck must survive export, projection, and conventional PPT review

### 2. Magazine-Like Long Narrative Density

Do not borrow:
- paragraph-heavy editorial pages
- visually dramatic but content-dense spreads

Reason:
- defense slides must be explainable quickly

### 3. Decorative Micro-Typography

Do not borrow:
- tiny helper labels
- tiny captions or submarks used only for visual flavor

Reason:
- academic projection conditions punish small text

### 4. Style Experiments That Obscure Evidence

Do not borrow:
- overly expressive compositions on result pages
- ornamental backgrounds behind charts
- graphic treatments that compete with method logic

Reason:
- research credibility depends on evidence legibility

## Operational Rules For This Skill

The skill should apply `guizang` selectively:
- borrow layout discipline, not novelty for novelty's sake
- borrow page-type thinking, not freeform aesthetic experimentation
- borrow cleaner hierarchy, not decorative microtext
- borrow premium opening rhythm, not dense body-page styling

## Minimum Readability Rule

For this skill:
- visible editable text should not go below `18px`
- in PowerPoint-native sizing this is treated as roughly `13.5pt`

If a layout would require smaller text:
- shorten the copy
- remove low-value labels
- split the page
- or increase the visual slot efficiency
