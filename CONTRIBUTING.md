# Contributing

Thanks for contributing.

## Scope

This repository is for the `academic-ppt` skill and its supporting scripts, references, and assets.

Good contributions usually fall into one of these categories:

- better thesis-defense planning logic
- clearer or more reliable source normalization
- improved editable slide generation
- stronger validation or error reporting
- documentation and attribution fixes

## Before You Change Anything Large

Open an issue or write a short proposal if you want to:

- replace the authoring backend
- restructure the skill contract in `SKILL.md`
- add or remove bundled third-party assets
- change repository licensing or attribution

## Development Expectations

- keep edits scoped to the skill's current purpose
- preserve editable output as a hard requirement
- prefer reproducible pipelines over manual one-off patches
- do not remove attribution for adapted upstream work
- update `THIRD_PARTY_NOTICES.md` when bundling or adapting new upstream material

## Validation

Before opening a PR, run the relevant local checks where possible:

- source normalization on a representative thesis folder
- deck planning
- PPTX generation
- render validation
- overflow validation
- font validation

If a check cannot be run locally, say so clearly in the PR description.

## Documentation

Update the documentation when behavior changes:

- `README.md` for repository-level usage changes
- `skill/academic-ppt/SKILL.md` for workflow or contract changes
- `CHANGELOG.md` for release-facing changes

## Licensing

By contributing, you agree that your contributions will be released under the MIT License used by this repository.
