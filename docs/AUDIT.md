# Checklist Design audit — 12stockIndex report

Reviewed artifact: `report/index.html` — a static research report / mini-dashboard for an equal-weight 12-stock PSX portfolio. Input was the source file plus a headless-Chrome DOM dump that confirmed every section renders (5 KPI cards, 12 table rows, chart SVG, sector bars). Auditing against the **Analytics (Web app)** checklist for the dashboard sections and the **Data Table (Web app)** checklist for the holdings table, kept separate.

⚠️ Several items concern how the page looks and behaves on screen. The code and the rendered DOM are verifiable; the pixels are not (no image input in this session). Rows that need a screenshot to settle are marked ❔.

## Analytics — Web app
Source: https://www.checklist.design/web-app/analytics

| | Item | Why |
|---|---|---|
| 🟡 | **Date range selector** — A date picker with shortcuts for today, last 7 days, last 30 days, this month, and custom range | Shortcut periods exist (3M / 6M / 1Y / All segmented control on the chart). No picker or custom range — a deliberate scope call for a static report; the shortcuts carry the whole load here. |
| 🟢 | **Headline metrics** — The most important numbers displayed as prominent headline figures | Five KPI cards (P/E 8.5x, ROE 23.9%, EPS growth +29.3%, yield 5.9%, 12M backtest +13.8%) plus the KSE-100 pulse card in the hero. |
| 🟢 | **Charts with labels and axes** — Visualisations with clearly labelled axes, a legend where needed, and readable tick marks | Main chart has y tick labels, x date ticks, and a two-line legend. The "rebased to 100" unit sits in the section heading rather than on the axis — fine at this size. |
| 🟢 | **Period comparison** — A percentage or absolute change indicator showing how each metric has moved relative to the prior period | Alpha strip gives 3M/6M/12M vs KSE-100 with percentage-point deltas; every KPI's sub-label compares against the index. |
| 🟡 | **Segment breakdown** — The ability to slice a metric by properties | Sector allocation bars + legends (portfolio vs index) break the book down by sector, but as a separate visualization rather than a slice control over the main chart. For a 12-name book that's the useful slice. |
| 🟢 | **Last updated indicator** — A visible timestamp or refresh button showing when the data was last updated | "Data as of 07-09-2026" chip pinned in the nav, repeated in the pulse card and footer. |
| ⚪ | **Loading and empty states** — Skeleton loaders while data is fetching, and a contextual message when no data exists | Not needed: all data is embedded JSON, nothing fetches, so there's no loading or empty state to design. |

## Data Table — Web app
Source: https://www.checklist.design/web-app/data-table

| | Item | Why |
|---|---|---|
| 🟢 | **Sortable columns** — Column headers that sort rows by that value on click, toggling ascending and descending | All ten data columns sort on click with ▲/▼ indicators and asc/desc toggling; numeric vs string sorting handled per column. |
| ⚪ | **Column visibility and order** — Controls to show or hide individual columns and drag to reorder them | Not needed: a fixed 10-column report table in a one-off artifact; nobody is personalizing or persisting column setups here. |
| ⚪ | **Row selection and bulk actions** — Checkboxes on each row and a persistent action bar appearing when rows are selected | Not needed: there is no bulk operation on a 12-row research table — no compare, export, or delete exists to trigger. |
| 🟡 | **Row actions on hover** — Contextual actions (edit, delete, view) appearing when hovering over a row | The one action that matters — opening the detail panel (thesis, risk, snapshot, sparkline) — is on click, not hover. Click-to-expand is the better call for keyboard and touch; no icon row, which is fine for a single action. |
| ⚪ | **Search and filter** — A search input for quick lookup alongside filter controls | Not needed at 12 rows; a search box would be noise, and column sorting already covers lookup. |
| ⚪ | **Pagination** — Controls to navigate between pages of results, with an option to choose how many rows show per page | Not needed: 12 rows, one page. The project's own table pattern only paginates at 20+ rows. |
| 🟡 | **Frozen columns** — The first column pinned so it remains visible when the user scrolls horizontally | Header is sticky; the symbol column isn't frozen. On desktop the table fits its container and never scrolls, so nothing is lost. On phones it scrolls horizontally and the identifier scrolls away — a `position:sticky; left:0` on the first column would finish it if the report gets mobile traffic. |
| ⚪ | **Export action** — A way to download the visible or selected rows as CSV, spreadsheet, or another format | Not needed as a product feature, but a CSV of the 12 holdings would be genuinely handy for someone acting on this — a nice-to-have, not a gap. |
| ⚪ | **Empty and loading states** — The states shown when the table has no rows or when data is being fetched | Not needed: data is embedded and synchronous; there is no state to show. |

## Beyond the checklist

- The y-axis carries no unit label — "rebased to 100" lives in the section heading and the footnote. Fine at this size; if this ever becomes a live dashboard, put the unit on the axis.
- Negative values are red and positives green in every number column, never used decoratively — the color discipline holds across the table, KPIs, and chart.
- One real accessibility fix already applied during review: the tertiary text color was lightened-then-darkened to clear WCAG AA on the smallest labels.

**To settle the ❔-adjacent visual questions** (spacing rhythm, hover states, the sliding tab indicator): open `report/index.html` in a browser — a two-minute eyeball pass will confirm them.
