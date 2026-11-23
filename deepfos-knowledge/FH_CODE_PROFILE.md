# FH Code Profile

- Generated: 2026-10-28
- Distillation source: `/Users/theo/Documents/Python_Code/FH`
- Storage location: `/Users/theo/Documents/codex_deepfos/deepfos-knowledge/FH_CODE_PROFILE.md`
- Purpose: preserve project-specific coding patterns for code generation in any conversation under the `codex_deepfos` workspace.
- Method: static AST scan only; no business scripts were executed.

## 1. Inventory

```text
Python files: 702
Python lines: 323,767
AST parse errors: 0
```

Top-level distribution:

| Folder | Python files |
|---|---:|
| `Dome` | 529 |
| `HRYS_rules` | 111 |
| `poc_rules` | 24 |
| `dsl` | 15 |
| `poc_lvye` | 12 |
| `poc_HRYB_rules` | 10 |
| root files | 1 |

## 2. Main code families

### A. `Dome/oa联动/vip-plan/rules`

This is the largest and most structured family.

- Uses async finance cubes through `rules.models.cubes.BaseCube`.
- Dimension members are exposed through `rules.models.dimensions`.
- Common helpers live in `rules.libs.common`.
- `BaseCube` extends `AsyncFinancialCube`, provides `query_diff`, custom `_save_impl`, and dimension helpers.
- Prefer this family's wrappers when editing code under `Dome/oa联动/vip-plan/rules`.

Key files:

```text
Dome/oa联动/vip-plan/rules/models/cubes.py
Dome/oa联动/vip-plan/rules/models/dimensions.py
Dome/oa联动/vip-plan/rules/models/dimension_model.py
Dome/oa联动/vip-plan/rules/libs/common.py
```

### B. `HRYS_rules`

- Direct DeepFOS SDK usage plus local `HRYS_rules.libs`.
- Has its own config model and SSO/fastapi components.
- `HRYS_rules/libs/common.py` is an exact duplicate of `dsl/libs/common.py`.
- `HRYS_rules/libs/patch.py` is an exact duplicate of `dsl/libs/patch.py`.

### C. `dsl`

- Smaller direct-SDK family.
- Uses `FinancialCubePatch` from `dsl/libs/patch.py`.
- Common helpers: `fill_columns`, `rename_period_columns`, `EntityMapping`, currency helpers.
- Rule files often expose `async def main(p1, p2)` and a `__main__` debug block.

### D. `poc_rules`, `poc_lvye`, `poc_HRYB_rules`

These are largely copies/forks of the same helper layers.

Exact duplicate groups include:

```text
poc_lvye/libs/common.py
poc_HRYB_rules/libs/common.py
HRYS_rules/libs/common.py
poc_rules/libs/common.py
dsl/libs/common.py

poc_lvye/libs/patch.py
poc_HRYB_rules/libs/patch.py
HRYS_rules/libs/patch.py
poc_rules/libs/patch.py
dsl/libs/patch.py
```

Do not treat duplicate copies as independent best practices. Inspect the target family first.

## 3. Dominant imports and patterns

Top import roots:

```text
rules      1190
deepfos    1143
pandas      567
asyncio     517
__debug     497
loguru      469
numpy       114
```

Common SDK modules:

```text
deepfos.element.finmodel
deepfos.element.datatable
deepfos.element.dimension
deepfos.lib.utils
deepfos.lib.asynchronous
deepfos.options
```

Core call frequency:

```text
dict_to_expr        921
query               776
delete              507
save_unpivot        469
select              437
fill_columns        377
asyncio.gather      786
insert_df           130-file occurrences
```

Element usage by file:

```text
FinancialCube()            129
AsyncFinancialCube()       128
DataTableMySQL()           298
AsyncDataTableMySQL()      291
save_unpivot()             173
```

## 4. Preferred implementation patterns

### Financial Cube read

- Build a POV dictionary and convert with `dict_to_expr`.
- Use `compact=False` when POV fields must remain as DataFrame columns.
- Use `pivot_dim="Period"` or `pivot_dim="Item"` when the downstream calculation needs wide columns.
- Use `pivot_members` when all output columns must exist even if source data is absent.
- Treat empty/None dimension values as invalid; use explicit members such as `NoEntity`, `NoStore`, `NoMisc`, `NoPeriod`, or omit only when the cube contract allows it.

### Financial Cube write

- Match the target family's wrapper first.
- Common sequence: query source -> transform -> delete target range -> save or save_unpivot.
- Use `save_unpivot` when Period/Item members are columns.
- Never pass the unpivot dimension itself in the fixed POV for `save_unpivot`.
- Drop helper columns such as `name`/`ud31` before unpivoting.
- Use `chunksize=5000` by default unless the target family uses another established chunk size.
- Use `delete`/`insert_null` only with an explicit target range and business confirmation.

### Dependent Financial Cube item chains

- When target items depend on other calculated target items, do not flatten the whole chain into one in-memory calculation.
- Process one dependency level at a time: query current cube data -> calculate the target item -> save it -> re-query cube before the next level.
- Preserve the business dependency order explicitly in the orchestration method and document it in comments.
- Do not optimize away intermediate saves or re-queries unless the cube contract explicitly guarantees equivalent in-memory consistency.
- Example order: `B010` save -> query `B010/B011/B012/B013` -> calculate and save `B014` -> query `B014/B015/...` -> calculate and save `B021`.

### DataTable

- Prefer project wrappers and existing config classes.
- Use `insert_df` for inserts; check the actual SDK version for update/upsert capabilities.
- Validate DataFrame columns against target schema before writing.
- Do not rely on column order; rely on column names.
- Handle nullable columns and type conversions explicitly when the SDK writer is strict.

### Async and concurrency

- Async rules should use `await` for SDK calls.
- Use `asyncio.gather` for independent reads.
- Use `ThreadCtxExecutor`/`split_dataframe` for large batches where already used in the family.
- Do not mix sync and async cube classes in the same path without a clear reason.

## 5. Useful local helpers

```text
dsl/libs/patch.py
  FinancialCubePatch
  query with pivot column filling
  save/save_unpivot
  delete/delete_parallel
  save_parallel/save_unpivot_parallel

dsl/libs/common.py
  CustomMethods
  EntityMapping
  fill_columns
  rename_period_columns
  currency and entity helpers

Dome/oa联动/vip-plan/rules/models/cubes.py
  BaseCube
  query_diff
  custom _save_impl
  dimension class access

Dome/oa联动/vip-plan/rules/libs/common.py
  fill_columns
  get_not_pivot_dim_list
  get_dim_expr_name_li
```

## 6. Entry point and debug patterns

Many rule files expose:

```python
async def main(p1, p2):
    obj = RuleClass(p1, p2)
    await obj.run()

if __name__ == "__main__":
    from __debug import init
    p1 = init("dsl", "dev")
    p2 = {...}
    asyncio.run(main(p1, p2))
```

Observed counts:

```text
files importing __debug: 497
files with __main__: 507
files with async def main: 548
```

Important: `FH/__debug.py` `init()` sets global OPTION values but does not return the header. Code that assigns `p1 = init(...)` gets `None`. Most rules do not use `p1`, but do not depend on it unless the target class requires it.

## 7. Security and do-not-copy rules

Static scan found secret-like references in 19 files, including debug headers, database/Redis config, and SSO components.

Never copy or generate real values from:

```text
FH/__debug.py
Dome/oa联动/vip-plan/__debug.py
Dome/主数据/PCI/pic/__debug.py
dsl/dbConn/config.py
dsl/dbConn/config_copy.py
HRYS_rules/libs/config.py
SSO/login/config/redis files
```

Do not include token, cookie, client_secret, password, access_token, or user identifiers in generated code or summaries. Use placeholders and reference configuration by name.

## 8. Known risks and anti-patterns

- Multiple exact copies of common/patch/dim/upload helper files across families.
- Hardcoded environment names, element IDs, POV values, and debug parameters in `__main__` blocks.
- Mixed `FinancialCubePatch`, `BaseCube`, direct `AsyncFinancialCube`, and sync SDK usage across families.
- `FinancialCubePatch` derives `entry_object` from `inspect.stack()` and is sensitive to call depth/move.
- Some directories contain spaces in names; imports may fail if path handling is not exact.
- Some direct config modules create connections at import time; avoid importing them casually in read-only analysis.
- `__debug.py` contains long-lived credentials and must not be copied into skills, profiles, or generated code.

## 9. Code-generation contract

When generating code for FH:

1. Identify the target family: `Dome/.../rules`, `HRYS_rules`, `dsl`, or a `poc_*` copy.
2. Inspect one or two existing scripts in the same folder before choosing imports.
3. Prefer the family's wrapper over a raw SDK class.
4. Preserve async/sync style and chunking conventions.
5. Use `dict_to_expr`, explicit POV values, and `compact=False` where the family does.
6. Use `save_unpivot` for wide Period/Item DataFrames and remove extra columns first.
7. Validate target schema, nullable fields, and key/update strategy before generating writes.
8. Never copy credentials or execute business scripts during static analysis.
9. Do not modify files without explicit user approval.
10. If behavior or signatures are uncertain, use the `deepfos-py-research` skill and SDK 1.1.94 source before generating code.

## 10. Reusable template backlog

The profile is sufficient for these future templates:

```text
financial-cube-read
financial-cube-read-wide-period
financial-cube-delete-save
financial-cube-save-unpivot
datatable-mysql-read-write
datatable-clickhouse-read-write
api-pagination-etl
dataframe-field-mapping
rule-main-debug-entry
```

Create these templates only after a real target task confirms the required shape.
