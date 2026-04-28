# agent.md

## Purpose

This file defines how human contributors and coding agents should contribute to **NRV**.
It is intentionally optimized for **agent execution and reviewability**, while remaining readable by maintainers.

NRV is a scientific Python framework for **peripheral nervous system stimulation modeling**, built around **NEURON** and finite-element workflows, with current open-science FEM work centered on **FEniCS/FEniCSx** rather than COMSOL. Contributions must therefore preserve **scientific traceability**, **reproducibility**, and **backward compatibility**. [NRV README](https://github.com/nrv-framework/NRV) [NRV docs](https://nrv.readthedocs.io/en/latest/) [PLOS paper](https://doi.org/10.1371/journal.pcbi.1011826)

## Scope

This file applies to the repository root and all work inside:

- `nrv/`
- `docs/`
- `examples/`
- `tests/`

It should also be followed when a change affects tutorials, build metadata, packaging, or documentation generation indirectly.

## Source of truth

- **Stable reference branch:** `master`
- **Secondary branch of interest:** `testability`
- `testability` is the branch currently used to introduce or consolidate:
  - unit tests
  - end-to-end tests
  - deployment-oriented validation
  - future CI/CD integration

When branch-specific behavior differs, prefer `master` for user-facing and scientific behavior, and use `testability` as the reference for emerging testing practices.

## Project principles

Every contribution to NRV must respect the following principles:

1. **Preserve scientific validity.**
   - Do not alter equations, model assumptions, physiological behavior, or numerical protocols casually.
   - Any modification involving equations must be grounded in a scientific source.

2. **Preserve traceability.**
   - Scientific ideas, equations, constants, and design choices should be attributable.
   - When possible, cite the source publication and DOI in comments, docstrings, or documentation.

3. **Preserve reproducibility.**
   - Randomized behavior must use explicit seeds where relevant.
   - Scientific changes should be validated against a benchmark, reproduced figure, tutorial, or reference result whenever feasible.

4. **Preserve backward compatibility.**
   - Existing public APIs and expected user workflows should continue to work unless a human explicitly approves a breaking change.

5. **Keep the library open-science oriented.**
   - Prefer free and reproducible tooling.
   - FEM development should prioritize the FEniCS/FEniCSx path.
   - COMSOL support may exist, but it is no longer the preferred direction for new development.

## Authority and escalation

### Changes an agent may perform without prior human approval

An agent may propose and implement changes directly when they are limited to:

- documentation
- tests
- moderate refactors
- non-breaking API improvements
- typing improvements
- code quality improvements
- examples and usage clarifications

These changes are still expected to satisfy the validation rules below.

### Changes that must always be escalated to a human

An agent must stop and request human review before finalizing any change that affects:

- the **public API** in a breaking or behavior-changing way
- **physiological or scientific models**
- **equations**
- **numerical methods** or solver logic with scientific impact
- **versioning**, **release steps**, or `bump2version`
- licensing or legal statements
- changes whose scientific correctness cannot be justified

### Sensitive area

Treat **all equations** as sensitive.
Any modification of equations, derived formulas, or model assumptions requires explicit scientific justification and human review.

## Branching and contribution workflow

### Branching model

- `master` is the stable reference branch.
- A future `dev` branch is expected to become the integration target for pull requests.
- Once `dev` exists, contributions should branch from it and merge back into it.

### Branch naming

Use explicit branch names derived from the integration branch and the change type.

Recommended patterns:

- `dev-feature-short-name`
- `dev-bugfix-short-name`
- `dev-doc-short-name`
- `dev-test-short-name`
- `dev-refactor-short-name`

### Pull requests

Prefer contributions linked to an existing GitHub issue whenever possible.
If no issue exists and the change is substantial, open or request one first.

## Definition of done

A contribution is not done unless all of the following are true:

- the code or function is implemented correctly
- the change includes a corresponding test
- docstrings are updated
- user-facing documentation is updated when relevant
- backward compatibility is preserved, unless a human approved otherwise
- the change is scientifically traceable when scientific content is involved

## Testing and validation

### Minimum validation

For any accepted contribution:

- run the relevant tests
- ensure formatting is clean
- ensure the code remains importable and coherent
- ensure docs/docstrings/examples remain aligned with behavior

### Testing policy by change type

- **API changes:** at minimum, add or update a focused automated test
- **Scientific changes:** run broader validation with stronger evidence
- **Bug fixes:** add a regression test whenever possible
- **Documentation-only changes:** verify that docs still build when documentation files are touched

### Reference test commands

The existing developer documentation documents the historical test launcher as:

```bash
cd tests
./NRV_test --syntax
./NRV_test --all
```

Use that path for legacy/scientific validation workflows.
For work aligned with the `testability` branch, `pytest`-based validation is also expected for API-oriented tests.

### Scientific validation requirements

For a scientific modification, include at least one of the following when relevant:

- a benchmark
- a reproduced figure or reproduced numerical result
- a comparison against an existing tutorial or example
- a comparison against published or previously validated behavior
- a dedicated validation note in the PR

Formal scientific verification is preferred whenever realistically possible.

### Performance expectations

No strict performance gate is required for ordinary contributions, but contributions should not introduce unreasonable slowdowns.
Long computations are acceptable when they remain scientifically justified and operationally practical.

## Code rules

### General expectations

- Use **Python type hints** wherever possible.
- Keep refactors **moderate**.
- Preserve readability over cleverness.
- Keep physical units explicit in comments, docstrings, or existing unit-handling utilities.
- Reuse existing project patterns before introducing a new abstraction.

### Dependencies

Prefer the existing scientific stack whenever feasible, especially:

- `numpy`
- `scipy`
- `pandas`
- `NEURON`
- `FEniCS/FEniCSx`
- `gmsh`

New dependencies are acceptable only when they are clearly necessary and justified.

### COMSOL policy

COMSOL is supported only as a secondary or legacy path.
Do **not** prioritize new COMSOL-first development.
For new finite-element development, prefer the FEniCS/FEniCSx workflow, which NRV documents and the project paper position as the open and validated direction. [NRV README](https://github.com/nrv-framework/NRV) [PLOS paper](https://doi.org/10.1371/journal.pcbi.1011826)

### Generated and non-Python artifacts

Do not commit incidental generated outputs, simulation by-products, or unrelated binary artifacts.
Be especially careful with non-Python files inside `_misc`, which may contain reference values, distributions, defaults, geometry assets, or other package data required by the library.

## Documentation rules

Documentation is mandatory.

When code changes affect users, update documentation accordingly.
At minimum:

- update docstrings
- update `docs/` content when behavior or usage changes
- update the `toctree` when adding a new documentation page
- add or update examples when introducing a new user-facing feature

Follow the structure described in the developer documentation:

- generic explanations in `docs/*.rst`
- examples in `examples/`
- tutorials in `tutorials/`
- API documentation through source docstrings

If a new feature is user-facing, include a **minimal example**.

## Compatibility and deprecation

- Backward compatibility is the default rule.
- Avoid renaming, removing, or silently changing public behavior.
- If deprecation is necessary, document it clearly in docstrings and user documentation.
- Do not introduce a breaking change without explicit human approval.

## Environments

A generic Linux development/documentation environment is described in the repository through `docs-env.yaml`.
Agents may assume the availability of the main scientific runtime stack, especially **NEURON**, **FEniCS/FEniCSx**, and **MPICH**, but should assume **COMSOL may be absent** and must not require it by default. [NRV repository](https://github.com/nrv-framework/NRV) [NRV docs](https://nrv.readthedocs.io/en/latest/)

## Reviews and communication

Changes requiring documentation evolution should be reviewed by the development team.

When unsure, use one of the project discussion channels instead of guessing:

- GitHub Issues
- GitHub Discussions
- the project Discord

When uncertainty concerns scientific correctness, escalate early.

## Releases and versioning

Agents must **not** perform releases autonomously.

In particular:

- do not initiate `bump2version`
- do not finalize version bumps without human initiation
- do not treat packaging metadata as authoritative when it conflicts with project policy without flagging it

Release-related documentation may lag behind packaging changes and should be checked carefully before any release-oriented edit.

## Legal and citation policy

Treat the project license as **CeCILL** for contributor guidance, and flag any repository metadata that still states otherwise for human correction.

Any equation or scientific method added or modified must be traceable to a scientific reference.
Whenever possible, include the publication reference and DOI.

If a contribution introduces a method that is not already documented in NRV documentation or literature references, request human scientific review.

## Preferred terminology

Use precise scientific language consistent with:

- computational neuroscience
- peripheral nerve stimulation
- numerical modeling
- reproducible scientific software

Avoid vague wording when documenting scientific behavior.

## Maintenance of this file

This file is owned by the **nrv-framework** GitHub organization.

It should be updated whenever one of the following changes:

- the branching model
- the testing workflow
- the release workflow
- the documentation workflow
- the preferred FEM stack
- the legal/licensing policy
- contribution governance

When this file conflicts with explicit human maintainer guidance in a PR or issue, follow the maintainer guidance and then update this file accordingly.
