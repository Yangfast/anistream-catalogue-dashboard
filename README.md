# AniStream Catalogue Dashboard

A Streamlit dashboard for **AniStream**, a streaming platform, built on the
[Anime Dataset 2026](https://www.kaggle.com/datasets/darkbarrierhub/anime-dataset-2026) Kaggle dataset.

**App:** _filled in after deployment_
**Built for:** Lin Lan, Content Procurement & Recommendation Strategy Manager

---

## Step 1 — The dataset and the decision-maker

### The dataset

| | |
| --- | --- |
| **Source** | [Anime Dataset 2026](https://www.kaggle.com/datasets/darkbarrierhub/anime-dataset-2026) on Kaggle |
| **Origin** | MyAnimeList (MAL) catalogue data: titles, scores, member counts, favourites, studios, genres, air dates |
| **Period** | Titles first aired **1917 – 2026** (snapshot taken in 2026) |
| **One row is** | one anime title — a series, film, OVA, special, music video or promotional clip |
| **Size** | 30,763 rows × 24 columns (19.3 MB raw) |
| **Real or synthetic** | Real scrape of user-generated data: scores are MAL **user ratings**, members are **lifetime MAL members** |
| **What I committed** | `data/anistream_shelf.csv`, 20,161 rows × 17 columns, **3.5 MB** — a filtered, column-trimmed version of the raw file (see *What was cut*, below) |

### The decision-maker

**Lin Lan, Content Procurement & Recommendation Strategy Manager.**

Before every Monday procurement call and every monthly purchasing meeting she screens the
catalogue across type, year, studio, status, score, Members and Favorites to decide three
things:

1. **Acquisition shortlist** — which titles to buy.
2. **Homepage slots** — which titles get promoted on the home page this week.
3. **Renewal list** — which existing licences to keep paying for.

She looks at the same questions every week: *which high-scoring titles also have a large audience?
which genres perform well overall? which studios deserve a batch deal? which high-traffic titles
have bad reception and only deserve a short-term slot?*

## Step 2 — Why this deserves a dashboard

1. **Who looks at it, and how often?** Lin Lan, **weekly** before the Monday procurement call and
   **monthly** before the purchasing meeting. It is also opened ad hoc when a licensor pitches.
2. **What decision does it support?** *"If Lin Lan sees that a high-scoring title has fewer than
   100k members, she will move it off the renewal list and keep it as a cheap catalogue title; if
   she sees a title with a large audience but a poor score, she will book it for a two-week
   homepage traffic slot instead of a renewal."* In practice she reads four numbers — titles in
   selection, median score, **anchor candidates**, **traffic-only titles** — and then filters to act.
3. **What does she do today without it?** She runs ad-hoc pandas queries in a notebook or reads a
   sortable spreadsheet. Each question ("which 2020+ thrillers scored above 7.5 with more than
   100k members?") is a new query, and two people asking the same question can get different
   answers because the score and audience cut-offs are re-typed each time. That costs an hour or
   two a week and produces inconsistent shortlists.
4. **Why a dashboard rather than an email or an alert?** An email is a frozen answer to one question;
   her questions repeat with **different filters each time** (this week a thriller, next week a
   studio). A dashboard lets her change the filter and keep the same comparability rules. An alert
   is the wrong shape too: nothing here is urgent — the decision happens on a schedule, not the
   moment a number moves.

## Step 3 — What is on the page, what was cut, and why

The page is ordered by importance, so that the top answers *"is anything wrong right now?"* and
everything below explains it.

### Top: the headline numbers (four `st.metric` in `st.columns`)

| Metric | What it counts | Why it is a headline |
| --- | --- | --- |
| **Titles in selection** | titles passing the filters | the size of the shelf she is choosing from |
| **Median score** | median user score of that shelf | *"is this selection worth buying at all?"* — one number to compare selections |
| **Anchor candidates** | score ≥ 7.5 **and** ≥ 100k members | the renewal/acquisition shortlist: quality a large audience has already found |
| **Traffic-only titles** | score < 6.5 **and** ≥ 100k members | the traps: big audience, bad reception — homepage slot, never a renewal |

The cut-offs are not arbitrary. On the 20,161-title shelf the median score is 6.39 and the median
audience is 4,102 members; **7.5** is close to the top decile of scores and **100,000 members** is
close to the top decile of audience. Picking the two *together* is what turns two long lists into
a shortlist: **1,186** titles clear both bars (5.9% of the shelf), and **206** are in the opposite
corner (1.0%).

### Middle: the charts that explain the number

1. **Audience vs. reception scatter (the hero chart).** One dot per title, audience on a log x-axis
   and score on the y-axis, with the two decision zones marked. This single chart answers three of
   her four recurring questions at once — *high score with a large audience* is the top-right,
   *high-traffic titles with bad reception* is the bottom-right, and hovering a dot shows the studio
   and type. It also makes the trade-off visible in a way four numbers cannot: the two groups are
   **not** separated by audience alone — both have large audiences, and the score is what splits
   them.
2. **Median score by format and by genre** (two bar charts). Answers *"which genres perform well
   overall?"* and exposes that **format** matters as much as genre: series median **6.69** against
   shorts **5.91**.
3. **Studio table** with a minimum-titles slider. Answers *"which studios deserve a batch deal?"*
   without the trap of a 2-title studio with a lucky 9.0 score: raise the threshold and only
   studios with a track record survive.

### Bottom: the detail

An expander with the actual shortlist (all / anchors only / traffic only), sortable and
downloadable as CSV, so she can paste the renewal list straight into the procurement deck.

### The filters (only what she actually uses)

A **type** selector, a **year range** slider, a **genre** selector and a **minimum audience**
slider. The last one is the important one: a title with 200 members cannot be judged on a 9.0
score, and hiding those titles is what makes every median on the page trustworthy.

### Two things I chose **not** to show

1. **The synopsis text, images and full cast/producer lists.** They were interesting in the EDA but
   they cannot change a procurement decision — a 300-word synopsis does not help rank 1,200
   candidates — and they would have turned the page into a catalogue browser.
2. **A raw count of titles by year, and the long tail of genres.** Both looked interesting in the
   EDA, but neither points at a decision: she never buys "a year", she buys titles. They would have
   pushed the scatter — the chart that actually answers her question — below the fold.

### What could mislead the viewer, and how the page handles it

| Trap | How the page handles it |
| --- | --- |
| **33.8% of the raw rows have no score** (10,405 of 30,763) | Those titles are removed before anything is counted, and the footer states the shelf is 65.5% of the raw rows. A title nobody scored cannot be judged. |
| **`Premiered` is `UNKNOWN` for 24,152 rows** (78%) | Year comes from the **`Aired`** date instead, which is known for 29,876 rows. Using `Premiered` would have silently dropped three quarters of the catalogue. |
| **`Studios` is `UNKNOWN` for 39%** of rows | The studio table says how many titles in the current selection carry a named studio, so a reader knows the comparison is partial. |
| **Score is a user rating on MyAnimeList, not AniStream viewing** | Stated in the footer: it is a **proxy for reception**, and Members are lifetime MAL members, not monthly streams. |
| **A 9.0 from 300 voters looks better than an 8.0 from 300,000** | Handled by the minimum-audience filter, defaulting to 1,000 members, and by the `Scored By`/`Members` columns in the detail table. |
| **Tiny studios with one lucky title** | The studio table has a minimum-titles slider (default 10). |
| **1950s–1980s catalogue is small and has incomparable audience numbers** | The year slider defaults to 1990 onward, and the help text says why. |

## Step 4 — Refresh frequency

1. **How often should the data be refreshed?** **Weekly**, on Sunday night, a full reload from the
   catalogue database. Not real time: the numbers she acts on are 7-day or lifetime aggregates, and
   the decision they feed happens once a week, so an hourly refresh would cost pipeline work and
   change nothing. One exception is worth automating: **Favorites velocity on titles currently in a
   homepage slot** would be checked daily, because a slot decision can be undone mid-week if the
   audience is not showing up.
2. **How often should someone review it?** Weekly, Monday morning, before the procurement call.
   Refreshing and reviewing are deliberately not the same: refresh is a data job, review is a
   meeting.
3. **What should be tracked over time, and what should trigger action?** The metric to track is the
   **count of anchor candidates**. I would also track each renewal candidate's audience **month over
   month**. **Trigger:** if a title on the current renewal list loses more than **20% of its members
   in a month**, or if a title's score drops below **7.0** while it still holds a homepage slot, that
   is a phone call — it is the signal that yesterday's anchor is becoming today's traffic-only
   title. Internally, an anchor candidate moving into the traffic-only corner is the single event
   this dashboard exists to catch.
4. **What does stale data cost?** A week stale is tolerable — she has one week to act anyway. A month
   stale is not: the headlines are drawn from a four-year window of titles and a renewals list that
   moves on seasonal cycles, so a month-old snapshot can present a title as an anchor after its
   audience has already moved on. That is the expensive error: renewing a licence at anchor prices
   for a title that is now a traffic-only title, or overbooking a homepage slot for a title users
   have stopped watching. The fixed cost of not refreshing is small; the cost of *acting on* an
   unrefreshed dashboard is one bad renewal.

**Data period and refresh, as shown on the dashboard:**
*Data: 1917 – 2026 (Kaggle snapshot, anime-dataset-2026). Refresh: weekly in production.*

## Step 5 — Build and deploy

```
anistream-dashboard/
├── app.py                        # the whole dashboard, one file
├── data/
│   └── anistream_shelf.csv       # 20,161 rows, 3.5 MB — the committed subset of the raw Kaggle file
├── requirements.txt
├── .streamlit/
│   └── config.toml               # headless server settings
└── README.md
```

* **Stack:** Python 3.14, Streamlit, pandas, Altair.
* **Deployed:** Streamlit Community Cloud, from this repository, `app.py` as the entry point.
* **How the committed CSV was made:** the raw 19.3 MB file was read, non-numeric score/rank fields
  coerced to numbers, the first-air date parsed out of `Aired`, and the file filtered to rows with
  **a positive score, a known first-air date, and `Status == "Finished Airing"`** — 20,161 rows, of
  which 17 columns are kept and the free-text and image columns dropped. The 3.5 MB result is
  committed instead of the raw file so that the repository and Streamlit Cloud stay small, as the
  exercise requires.

### Reproducing the data cut

```python
import pandas as pd

df = pd.read_csv("anime-dataset-2026.csv", low_memory=False)
for c in ["Score", "Episodes", "Rank", "Scored By"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")
df["aired_start"] = pd.to_datetime(
    df["Aired"].astype("string").str.split(" to ").str[0], errors="coerce", format="mixed")
df["year"] = df["aired_start"].dt.year

shelf = df[df["Score"].gt(0) & df["aired_start"].notna() & df["Status"].eq("Finished Airing")]
# ... rename, group types, take the first studio, keep 17 columns ...
```
