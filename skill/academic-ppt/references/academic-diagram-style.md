# Academic Diagram Style

## Goal

Academic diagrams should support explanation, not compete with it.

The figure must remain legible when:
- viewed at normal zoom
- placed on an A4 page
- inserted into a thesis chapter with a standard caption

## Core Style Rules

- Prefer white or very light backgrounds.
- Use low-saturation accent colors.
- Use consistent line weight and corner radius.
- Keep spacing regular and grid-aligned.
- Reduce decorative effects such as heavy shadows or glossy gradients.
- Use one dominant reading direction for the entire figure where possible.
- Keep semantic color usage sparse and consistent.

## Typography

- Node text should be short.
- Prefer concise noun phrases over sentence-style prose.
- Avoid squeezing long explanations into one box.
- If text becomes small, reduce wording before expanding complexity.
- Prefer a clean sans-serif font family and keep it consistent.
- Main node text should usually stay around 14-16 pt equivalent.
- Secondary labels should usually stay around 12-14 pt equivalent.
- Avoid going below roughly 12 pt equivalent in the final A4-ready figure.
- Make titles and major group labels clearly larger than ordinary node labels.
- Increase box size before shrinking text into an unreadable range.

## Layout

- Keep a clear primary reading direction.
- Separate major layers with whitespace, not visual clutter.
- Avoid excessive crossing connectors.
- Keep module widths and heights visually balanced.
- Keep adjacent nodes typically separated by about 24-40 px at starter-canvas scale.
- Keep major grouped sections typically separated by about 40-80 px.
- Use labeled containers or background bands when grouping related modules.
- Route connectors so they do not pass through text or box interiors unnecessarily.
- Adjust elbow points and connector bends manually when auto-routing looks awkward.
- Prefer clean orthogonal connector paths for structured academic diagrams unless another style is clearly better.
- Move nodes to improve line clarity instead of accepting tangled connector paths.

## Shape And Line Defaults

- Keep comparable nodes at comparable sizes unless size encodes meaning deliberately.
- Use consistent border widths for comparable objects.
- Use consistent arrowhead style for the same relationship type.
- Avoid mixing too many shape grammars in one figure; use shape variation only when it conveys structure.
- Keep corner radius consistent across similar boxes.

## Export Defaults

- Export PNG with a white or very light opaque background by default.
- Target publication-ready export size; roughly 2200 px or more on the longer side is a good default.
- Keep a small outer margin around the content.
- Ensure nothing is clipped at the export boundary.
- Prefer a figure that is slightly spacious over one that is densely packed.

## Readability Checklist

- Can the title and all main labels be read at normal page zoom?
- Are secondary labels still readable without zooming in heavily?
- Does each box contain one idea rather than a paragraph?
- Are connector directions obvious without verbal explanation?
- Does the figure still make sense in black-and-white print?
- Do connector bends and intersections remain easy to follow at normal size?
- Are arrowheads and line endpoints unobstructed?
- Is the exported PNG ready to insert into the paper without further cleanup?
- Are spacing, border widths, and arrow styles consistent across comparable elements?
- Is the figure readable without relying on color alone?

## Visual Differentiation

Different figure types should not look interchangeable.

- Architecture diagrams should emphasize modules and interactions.
- Roadmaps should emphasize stages and progression.
- Process figures should emphasize order and branching.
