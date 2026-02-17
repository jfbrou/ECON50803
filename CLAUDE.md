# ECON50803 -- Macroeconomic Environment (MBA, HEC Montréal)

## Project Overview

New MBA macroeconomics course taught in **English** by Professor Jean-Félix Brouillette. The course adapts and improves upon Nicolas Vincent's existing French-language MBA course (ECON50800, last taught Fall 2025) combined with elements from the undergraduate course ECON20852.

**Key design principles:**
- **Bilingual:** English and French versions of each session (symmetric EN/FR layout)
- LaTeX Beamer slides (Vincent uses PowerPoint)
- Sleek, business-oriented visual style (not academic)
- Updated to 2026 data and events
- Combines MBA-level framing with undergraduate analytical depth

## Course Structure

6 sessions (Vincent had 5 in 2025):

| Session | Topic | Vincent Session |
|---------|-------|-----------------|
| S1 | GDP, inflation, living standards | Séance 1 |
| S2 | Long-run economic growth | Séance 1 (part 4) + Séance 2 |
| S3 | Labor market, inequality, AI | Séance 2 + Séance 3 |
| S4 | Money, inflation, business cycles | Séance 3 + Séance 4 |
| S5 | Monetary and fiscal policy | Séance 4 + Séance 5 |
| S6 | Financial markets, international | Séance 5 + Séance 6 |

## File Structure

```
ECON50803/
├── CLAUDE.md              # This file
├── Slides/
│   ├── preamble.tex       # Shared Beamer template (all sessions import this)
│   ├── Figures_EN/        # English-labeled figures (+ static images shared by both languages)
│   ├── Figures_FR/        # French-labeled figures (falls back to Figures_EN/ for static images)
│   ├── Tables/            # Shared tables directory
│   ├── Data/              # Shared data files (e.g., tariff_data.xlsx)
│   ├── S1/
│   │   ├── EN/            # English: s1.tex, figures_s1.py
│   │   └── FR/            # French:  s1_fr.tex, figures_s1_fr.py
│   ├── S2/                # Sessions 2-6 (to be created, same EN/FR layout)
│   ├── S3/
│   ├── S4/
│   ├── S5/
│   └── S6/
```

## Compilation

Each session compiles independently from its language subdirectory:

```bash
cd Slides/S1/EN && pdflatex s1.tex        # English
cd Slides/S1/FR && pdflatex s1_fr.tex      # French
```

Build artifacts (`.aux`, `.log`, `.nav`, `.out`, `.snm`, `.toc`, `.fls`, `.fdb_latexmk`) are git-ignored.

## Bilingual Workflow

Each session has symmetric EN/ and FR/ subdirectories:
- **English slides** (`s1.tex`) use `\graphicspath{{../../Figures_EN/}}`
- **French slides** (`s1_fr.tex`) use `\graphicspath{{../../Figures_FR/}{../../Figures_EN/}}` -- French figures first, English fallback for static images (headshot, logos, external screenshots)
- **French figure generator** (`figures_s1_fr.py`) outputs to `Slides/Figures_FR/` with French axis labels, legends, and annotations
- **French slides** override the footer ("Environnement macroéconomique") and box default titles ("Point clé", "Définition", "Implication d'affaires", "Exercice") via `\RenewTColorBox`
- Source attributions, mathematical notation, and character names stay in English in both versions

## Nicolas Vincent's 2025 Slides (Reference Material)

**Location:** `/Users/jfbrou/Dropbox/MBA 2025/`

### Directory structure:
- `Diapos - MBA temps plein A2025/` -- All 6 session PPTX files (updated Oct 2025)
  - `MBA_2025_séance1_nv_v1.pptx` through `MBA_2025_séance6_nv_v1.pptx`
- `Séance 1/` through `Séance 6/` -- Individual session folders with:
  - PDF versions, PPTX versions, "material only" versions
  - Some folders have lecture recordings (MP4)
  - Some have supplementary articles (e.g., hot-charts, WSJ articles)
- `À changer pour 2025.docx` -- Vincent's notes on what to change for 2025
- `À changer pour 2026.docx` -- Vincent's notes on what to change for 2026
- `Examen/` -- Past exams
- `Quiz/` -- Quiz materials
- `Chine/` -- China case study materials
- `Notes et équipes/` -- Grading and team info

### Vincent's 2025 Session 1 structure (63 slides):
1. **Intro/Vue d'ensemble** (slides 1-12): Title, what is macro, why care, headlines collage, current events narrative (pandemic → inflation → rate response → tariffs → uncertainty → long-term growth)
2. **Organisation du cours** (slides 13-22): Objectives, agenda, teaching team, personal slides (Bank of Canada role), grading, materials
3. **Mesurer la production et les prix** (slides 23-54):
   - GDP definition, 3 approaches, expenditure components, NX explanation
   - Numerical exercises (updated to 2025/2026)
   - GDP decomposition by country (2023 data)
   - Can we trust GDP? (China transparency, US data integrity, night lights)
   - Real vs nominal GDP, GDP growth rate
   - **NEW in 2025:** Canada vs US GDP per capita (declining living standards), GDP contraction Q2 2025, tariff impact on exports, data integrity (Trump fired BLS head, jobs revisions)
   - Inflation definition, CPI, Bank of Canada target
   - **NEW in 2025:** Carbon tax removal impact, core inflation detail, online price collection (Cavallo et al. tariff tracker)
4. **Comparer les PIB des pays** (slides 55-63): Market exchange rates vs PPP, China vs US, Big Mac Index

### Key differences from 2021 version:
- Course code changed to ECON50803
- Agenda reduced from 6 to 5 topics
- Major new content on Trump tariffs (FT progression chart, employment impacts, GDP contraction)
- New content on data integrity (BLS firing, jobs revisions)
- New Canada vs US GDP per capita comparison
- Carbon tax removal impact on CPI
- Online price tracking (PriceStats tariff tracker)
- Vincent is now external deputy governor of the Bank of Canada
- Updated figures: IMF WEO July 2025, GDP decomposition 2023, CPI through 2025

## Beamer Template Conventions (preamble.tex)

### Colors
- `HECnavy` (#002855): Primary color -- titles, headings, structure
- `HECgreen` (#26d07c): Accent -- section divider rules, key insights
- `HECcoral` (#ff585d): Alert/warning accent
- `HECgray` (#94A3B8): Secondary text, sub-bullets, footer
- `HEClightgray` (#F1F5F9): Background for definition boxes

### Custom slide types
- `\titleframe` -- Title slide with navy sidebar
- `\sectionframe{Title}` -- Full-navy section divider
### Custom box environments (all use `arc=8pt` rounded corners)
- `\begin{keyinsight}[title]` -- Green accent, for key economic insights
- `\begin{bizimplication}[title]` -- Navy accent, for business relevance
- `\begin{warning}[title]` -- Coral accent, for important caveats
- `\begin{defbox}[title]` -- Gray background, for definitions

### Slide layout tips
- Use `[t]` frame option for slides with columns or variable content
- Use `\small` or `\footnotesize` when content is dense
- Placeholder figures use gray `tcolorbox` with `arc=8pt` (rounded corners) and a centered italic label
- Footer shows "ECON50803 | Macroeconomic Environment" + slide number (EN) or "Environnement macroéconomique" (FR)
- `\graphicspath{{../Figures_EN/}}` -- Default in preamble; overridden per-session in EN/ and FR/ subdirectories
- TODO comments mark figure placeholders that need actual images

## How to Adapt Vincent's Slides for Each Session

### General approach:
1. **Read the Vincent PDF** for the relevant session(s)
2. **Translate to English** -- not literal translation, but natural English phrasing
3. **Keep the core pedagogical structure** -- Vincent's flow is well-tested with MBA students
4. **Update data to 2026** -- Check if figures/examples reference outdated years
5. **Add depth from ECON20852** where appropriate -- more analytical rigor, additional exercises
6. **Use Beamer boxes** to highlight key insights, business implications, and warnings
7. **Add figure placeholders** with detailed TODO comments specifying source and content
8. **Maintain business framing** -- every concept should connect to business decisions

### What to keep from Vincent:
- Headlines/news hook at the start of relevant sections
- Numerical GDP accounting exercises
- Multi-country GDP decomposition charts
- "Can we trust GDP?" narrative (China + night lights)
- PPP / Big Mac Index for cross-country comparison
- The "not technical, not abstract, not ideological" positioning

### What to add beyond Vincent:
- More explicit connection of concepts to business decisions (bizimplication boxes)
- Clearer key insights (keyinsight boxes) after each major concept
- Definitions in structured defbox environments
- "Before next class" reading suggestions

### What to omit from Vincent:
- Personal slides (teaching team photos, "Mon autre vie", Bank of Canada role)
- French-specific examples where English equivalents are better
- Course logistics slides (grading, ZoneCours) -- handle these separately
- Redundant agenda slides between each sub-section

## Session-Specific Notes

### Session 1 (completed -- EN + FR)
- 78 pages (EN and FR), covers GDP + inflation + living standards + 2026 landscape
- Adapted from Vincent Séance 1 (minus growth section, which moves to S2)
- Added: data integrity slides, Canada vs US GDP per capita, tariff impact slides, core inflation slide, PriceStats tariff tracker
- 26 matplotlib figures generated by `figures_s1.py` (EN) / `figures_s1_fr.py` (FR)

### Sessions 2-6 (to be created)
- Review Vincent's slides for each corresponding session
- Follow the same template and conventions as S1
- Each session should have EN/ and FR/ subdirectories with symmetric structure
- Each session should be 40-50 slides
