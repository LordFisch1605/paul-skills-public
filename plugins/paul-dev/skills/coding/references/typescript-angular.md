# TypeScript and Angular 22

The Angular style guide at angular.dev and Angular's AI-assistant guidance page are the authority
for Angular; the Google TypeScript Style Guide for the language. The project's Prettier and
ESLint config, and its existing code, win over both.

## Toolchain, September 2026

- Angular 22 is current stable (22.1.x). Requires TypeScript `>=6.0.0 <6.1.0` and Node
  `^22.22.3 || ^24.15.0 || ^26.0.0`.
- Zoneless change detection is the default since v21; `OnPush` is the default strategy since v22
  — neither is set explicitly.
- `resource()`/`httpResource()` are stable since v22.
- Lint: `ng lint` via angular-eslint/typescript-eslint; `recommended-type-checked` is baseline.
- Format: Prettier. New CLI projects generate a config (printWidth 100, singleQuote, angular
  parser for `.html`). Run `npx prettier --write` on touched files; never hand-format.
- `tsconfig`: `strict: true` enables noImplicitAny, strictNullChecks, strictFunctionTypes,
  strictBindCallApply, strictPropertyInitialization, noImplicitThis, alwaysStrict,
  useUnknownInCatchVariables, strictBuiltinIteratorReturn. `noUncheckedIndexedAccess` is separate,
  worth enabling. CLI scaffold also sets `strictTemplates`.
- Unit tests: whatever runner `angular.json` names under `ng test` — current default is Vitest,
  Karma is legacy. Check `angular.json`, don't assume.
- Scaffold: `ng new <name> --defaults --style=scss --ssr=false`; backend calls go to relative
  `/api/...`.

## Conventions

- File matches the class identifier in kebab-case (`UserProfile` in `user-profile.ts`); the guide
  no longer mandates `.component.ts`/`.service.ts` suffixes — follow what the project uses.
- `inject()` instead of constructor injection.
- `protected` for members only the template reads; `readonly` for inputs, outputs and queries.
- Lifecycle hooks stay short; logic lives in named methods they call.
- Standalone is the default; never write `standalone: true`; no NgModules in new code.
- Signals for state: `signal()`, `computed()`, `linkedSignal()`; `input()`, `output()`, `model()`
  instead of decorators; change with `.set()`/`.update()`, never `.mutate()`.
- Native control flow `@if`, `@for`, `@switch`; `@for` requires `track` (NG5002 without one).
- Host bindings live in the decorator's `host: {}` object, not `@HostBinding`/`@HostListener`.
- Import only the directives and pipes the template uses, not `CommonModule`; `[class.x]`/
  `[style.x]` bindings, not `ngClass`/`ngStyle`.
- `takeUntilDestroyed()` in an injection context, or pass a `DestroyRef` elsewhere; prefer
  `httpResource` or a signal over a manual `subscribe` when the template reads the value.
- `unknown` over `any`; no `!` assertions, no `as` casts to silence the compiler — narrow at
  runtime instead.
- Named exports only, no default exports; arrow functions for callbacks, `function` at top level.
- `const` by default, `let` when reassigned, never `var`.
- camelCase for variables/functions, PascalCase for classes/interfaces/types/enums; no `I` prefix,
  no Hungarian notation.

## Testing

- Spec files `*.spec.ts` next to the unit; runner is whatever `angular.json` names.
- Services: instantiate directly or `TestBed.inject`; components: `TestBed`, assert via
  `fixture.nativeElement`, not private fields.
- `ng test` for the whole project before reporting, not one spec.

## What AI code gets wrong here

| Does | Instead |
|---|---|
| Generates NgModules or writes `standalone: true` | Standalone components, no flag |
| Constructor injection | `inject()` |
| `*ngIf`, `*ngFor`, `*ngSwitch` | `@if`, `@for`, `@switch` |
| `@Input()`/`@Output()` decorators | `input()`/`output()`/`model()` |
| Sets `changeDetection: ChangeDetectionStrategy.OnPush` | Nothing — it is the default in v22 |
| `@HostBinding`/`@HostListener` | The `host` object |
| Imports `CommonModule` | The specific directives and pipes used |
| `ngClass`/`ngStyle` | `[class.x]`/`[style.x]` |
| `.mutate()` on a signal | `.update()` or `.set()` |
| `@for` without `track` | `track item.id` |
| `as Foo` or `x!` to silence an error | A type guard or a null check |
| `any` | `unknown`, then narrow |
| Hard-coded `http://localhost:8080/api/...` | Relative `/api/...` |

## Sources

- Angular style guide: https://angular.dev/style-guide
- Angular, develop with AI: https://angular.dev/ai/develop-with-ai
- Angular version compatibility: https://angular.dev/reference/versions
- Angular zoneless guide: https://angular.dev/guide/zoneless
- Angular control flow: https://angular.dev/guide/templates/control-flow
- Angular takeUntilDestroyed: https://angular.dev/ecosystem/rxjs-interop/take-until-destroyed
- Google TypeScript Style Guide: https://google.github.io/styleguide/tsguide.html
- typescript-eslint configs: https://typescript-eslint.io/users/configs/
- TypeScript `strict`: https://www.typescriptlang.org/tsconfig/#strict
