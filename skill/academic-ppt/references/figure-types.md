# Figure Types

## System Architecture

Use this figure type when the reader needs to understand:
- what modules exist
- how modules relate
- where data enters and leaves
- how runtime responsibilities are divided

Typical node types:
- data source
- preprocessing layer
- model layer
- retrieval layer
- output or application layer

Quality cues:
- group major subsystems clearly
- show boundaries and interaction paths, not procedural chronology
- avoid turning the architecture into a step-by-step flowchart

## Technical Roadmap

Use this figure type when the reader needs to understand:
- how the study progresses
- how one stage leads to the next
- what each stage produces
- where validation appears in the sequence

Typical structure:
- stage
- key task
- stage output

Quality cues:
- keep progression visually directional and stage-based
- limit stage count to a readable set instead of chaining every minor step
- make outputs visible at the end of each major stage where relevant

## Workflow / Process

Use this figure type when the reader needs to understand:
- ordered steps
- branching conditions
- loops
- trigger and fallback logic

Typical node types:
- start
- process
- decision
- fallback
- output

Quality cues:
- make branching explicit
- label ambiguous decisions
- keep loops readable without tangled back-edges

## Granularity Rule

Before drawing, ask:
- Is this figure explaining structure, progression, or execution?

If the answer is:
- structure: use architecture
- progression: use roadmap
- execution: use workflow

Do not collapse all three into one overloaded figure.

If a figure starts trying to explain structure, chronology, and detailed control flow at the same time, split it into two figures.
