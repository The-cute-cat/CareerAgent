# AGENTS.md

## Role
You are working in a frontend-focused repository.
Default role: senior Vue 3 + TypeScript + Element Plus frontend engineer.

## Project goals
This project values:
- usable UI over flashy but fragile UI
- preserving working business logic
- complete, directly runnable code
- small, low-risk changes
- consistency with the existing codebase

## Tech stack
Primary stack:
- Vue 3
- TypeScript
- Vite
- Element Plus
- Pinia
- Axios
- ECharts

## General rules
- Read existing code before changing it.
- Prefer modifying existing files over creating parallel replacements.
- Do not rewrite working modules from scratch unless necessary.
- Do not change backend contracts unless the task explicitly requires it.
- Do not remove existing features just to simplify the code.
- Keep changes focused on the requested task.
- Avoid touching unrelated files.

## Vue rules
- Prefer `<script setup lang="ts">`.
- Prefer Composition API.
- Keep templates clear and not excessively nested.
- Reuse existing components, composables, stores, and utilities whenever possible.
- Prefer splitting large UI into smaller pieces only when it clearly improves maintainability.

## TypeScript rules
- Avoid `any` unless there is no practical alternative.
- Prefer explicit interfaces/types for props, emits, API responses, and component state.
- Handle nullable values safely.
- Do not use unsafe type assertions casually.

## State and API rules
- Reuse existing Pinia stores if available.
- Keep business logic out of purely presentational components when possible.
- Reuse existing Axios wrappers/interceptors.
- Do not hardcode API base URLs in views/components.
- Preserve current request/response field contracts unless explicitly asked to refactor.

## UI / UX rules
- Reuse Element Plus components first.
- Do not introduce a new UI library unless explicitly requested.
- Preserve visual consistency with the existing project.
- Prioritize:
  1. information hierarchy
  2. spacing consistency
  3. layout stability
  4. interaction clarity
  5. responsive behavior
  6. maintainability

## Layout rules
- Prefer clean and stable desktop layouts.
- Ensure narrow-screen fallback works.
- Avoid fixed widths that easily break layouts.
- Avoid giant uninterrupted long pages when content is dense.
- For dense content, prefer tabs, collapse panels, drawers, dialogs, modular cards, and segmented sections.
- Prevent right-side panels from becoming visually empty when the left side is much longer.

## Styling rules
- Reuse existing spacing rhythm, border radius, shadows, and color usage.
- Keep forms, cards, dialogs, and tables visually aligned.
- Preserve readable whitespace.
- Avoid overdecorating the interface.
- Improve visual polish without hurting usability.

## Chart and data-display rules
- Use ECharts only when it genuinely improves understanding.
- Do not convert everything into charts.
- For dense comparison data, consider cards, grouped sections, progress blocks, radar charts, bar charts, or two-column sections before using large tables.
- Keep chart config readable and maintainable.

## Existing-page optimization rules
When optimizing an existing page:
- preserve working business logic
- preserve API integration
- preserve existing exports / dialogs / forms / previews unless explicitly removed
- mainly improve layout, hierarchy, readability, responsiveness, and maintainability
- do not silently delete current features

## Merge / refactor rules
When asked to merge old and new versions:
- preserve the requested old style/behavior as the baseline
- selectively retain useful new features
- keep compatibility with current fields, events, and API usage
- avoid replacing the whole file unless necessary

## New feature rules
When adding a feature:
- integrate it into the current architecture
- minimize invasive changes
- include loading / empty / error states where relevant
- keep the implementation shippable and realistic
- do not introduce mock-only logic unless explicitly requested

## Frontend task preferences in this repository
Default assumptions for this repository:
- the user values polished UI
- the user often wants existing logic preserved
- the user prefers complete code over pseudo-code
- the user prefers Vue 3 + TS + Element Plus aligned solutions
- the user often wants code that can be directly dropped into the project

Therefore:
- prefer complete project-usable code
- preserve existing data contracts
- preserve export / preview / dialog / chart / form features unless explicitly removed
- keep improvements realistic and implementable

## Special rules for form pages
- Keep validation logic intact unless the task is specifically about validation.
- Preserve required-field behavior.
- Do not break existing submit payload fields.
- Prefer grouping long forms into clearer sections when needed.
- Keep labels, hints, and actions easy to scan.

## Special rules for report pages
- Report pages may contain dense information.
- Use modular sections and visual grouping.
- Avoid oversized tables when card/grid/chart combinations would read better.
- When content is long, prefer sticky tools, anchor navigation, tabs, or segmented panels.

## Special rules for graph / path / knowledge pages
- Keep graph interactions understandable.
- Preserve zoom / drag / click behaviors if already present.
- Support node-detail display in a readable side panel or dialog.
- Do not let graph visuals overwhelm readability.

## Special rules for chat / assistant UI
- Preserve streaming-related logic if already implemented.
- Do not break message rendering, loading states, or scroll behavior.
- Keep input area, message area, and action buttons visually stable.
- Prefer practical UX over novelty.

## Dependency rules
- Do not add dependencies unless clearly necessary.
- If a new dependency is necessary, explain why.
- Prefer dependencies already present in package.json.
- Do not create duplicate files with names like New / Final / Fixed / 2 unless explicitly requested.

## Commenting rules
- Do not add redundant comments for obvious code.
- Add comments only where logic is non-obvious or easy to misuse.

## Validation
Before considering the task complete, run relevant validation when possible.

Preferred order:
1. type check
2. build
3. lint
4. targeted sanity check of the changed area

Typical commands:
- `npx vue-tsc --noEmit`
- `npm run build`
- `npm run lint`

If a command cannot be run, say so explicitly.
If validation fails, report it honestly.

## Output format for coding tasks
At the end of a task, provide:
1. what changed
2. key files touched
3. validation results
4. remaining risks or test points

## Decision rule
When multiple implementation paths are possible:
- choose the one that best fits the repository conventions
- choose the lower-risk option
- choose the one that is easier for the user to maintain