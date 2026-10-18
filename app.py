"""AniStream catalogue dashboard — content procurement, homepage slots and renewals.

Built for AniStream's content procurement and recommendation strategy manager (Lin Lan), who
screens catalogues by genre, year, studio, status, score and audience before the weekly and
monthly procurement meetings.

Run locally:  streamlit run app.py
"""

from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

# ---------------------------------------------------------------- configuration

DATA_PATH = Path(__file__).parent / "data" / "anistream_shelf.csv"

# The two threshold pairs that define the decisions this dashboard supports. Chosen from the EDA:
# 7.5 is roughly the top decile of scores on the shelf, and 100k members is roughly the top decile
# of audience. See README.md.
ANCHOR_SCORE, ANCHOR_REACH = 7.5, 100_000     # renewal / acquisition candidates
TRAFFIC_SCORE, TRAFFIC_REACH = 6.5, 100_000   # high reach, poor reception -> short-term slots

DATA_PERIOD = (
    "Data: 1917-2026 (Kaggle snapshot, anime-dataset-2026). Refresh: weekly in production."
)

st.set_page_config(page_title="AniStream Catalogue Dashboard", page_icon="tv", layout="wide")


# ---------------------------------------------------------------- data

@st.cache_data(show_spinner=False)
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["genres"] = df["genres"].fillna("")
    return df


raw = load_data(str(DATA_PATH))

# ---------------------------------------------------------------- filters (sidebar)

st.sidebar.header("Filters")

type_options = ["Series", "Film", "Home video", "Short"]
type_choice = st.sidebar.radio(
    "Catalogue type",
    ["All types"] + type_options,
    help="Series and Film are what the homepage slots and renewals are about; "
         "Short covers music videos, trailers and promotional clips.",
)

year_min, year_max = int(raw["year"].min()), int(raw["year"].max())
year_range = st.sidebar.slider(
    "Release year of first airing",
    min_value=year_min, max_value=year_max,
    value=(1990, year_max),
    help="Defaults to 1990 onward: before that the catalogue is small and the audience "
         "numbers are not comparable with today's.",
)

genre_options = sorted(
    {g.strip() for value in raw["genres"] for g in str(value).split(",") if g.strip()}
)
genre_choice = st.sidebar.selectbox("Genre", ["All genres"] + genre_options)

min_members = st.sidebar.select_slider(
    "Minimum audience (MAL members)",
    options=[0, 1_000, 10_000, 100_000, 500_000],
    value=1_000,
    format_func=lambda v: "any" if v == 0 else f"{v:,}",
    help="Hides titles nobody has watched yet. A title with 200 members cannot be judged on "
         "a 9.0 score.",
)

st.sidebar.caption(DATA_PERIOD)

# ---------------------------------------------------------------- apply filters

view = raw.copy()
if type_choice != "All types":
    view = view[view["type_group"] == type_choice]
view = view[view["year"].between(*year_range)]
if genre_choice != "All genres":
    view = view[view["genres"].str.contains(genre_choice, regex=False)]
view = view[view["members"] >= min_members]

anchor_mask = (view["score"] >= ANCHOR_SCORE) & (view["members"] >= ANCHOR_REACH)
traffic_mask = (view["score"] < TRAFFIC_SCORE) & (view["members"] >= TRAFFIC_REACH)

n_titles = len(view)
n_anchor = int(anchor_mask.sum())
n_traffic = int(traffic_mask.sum())
median_score = view["score"].median() if n_titles else float("nan")

# ---------------------------------------------------------------- header

st.title("AniStream — Catalogue Screening for Procurement, Slots and Renewals")
st.caption(
    "For Lin Lan, content procurement and recommendation strategy manager. "
    "Screening decision: **which titles to shortlist for acquisition, which get a homepage "
    "slot, and which are renewed** — sorted by type, year, studio and audience."
)

if n_titles == 0:
    st.warning("No titles match these filters. Widen the year range or lower the minimum audience.")
    st.stop()

# ---------------------------------------------------------------- headline metrics

c1, c2, c3, c4 = st.columns(4)
c1.metric(
    "Titles in selection",
    f"{n_titles:,}",
    help="Titles that pass the filters. Airing and unscored titles are never in this count.",
)
c2.metric("Median score", f"{median_score:.2f}")
c3.metric(
    "Anchor candidates",
    f"{n_anchor:,}",
    help=f"Score >= {ANCHOR_SCORE} and >= {ANCHOR_REACH:,} members: high quality that a large "
         "audience has already found. Shortlist for acquisition and renewals.",
)
c4.metric(
    "Traffic-only titles",
    f"{n_traffic:,}",
    help=f"Score < {TRAFFIC_SCORE} but >= {TRAFFIC_REACH:,} members: a big audience and a poor "
         "reception. Use for short-term homepage traffic, do not build a renewal on them.",
)

if n_anchor == 0 and n_traffic == 0:
    st.info(
        "No title in this selection clears the audience threshold in either segment. "
        "Lower **Minimum audience** in the sidebar to see the shortlist."
    )

# ---------------------------------------------------------------- hero chart

st.subheader("Audience vs. reception — where each title sits")
st.caption(
    f"One dot per title. The two decision corners are: **top-right** = score >= "
    f"{ANCHOR_SCORE} with >= {ANCHOR_REACH:,} members (anchor), **bottom-right** = score < "
    f"{TRAFFIC_SCORE} with >= {TRAFFIC_REACH:,} members (traffic only). "
    "Log scale on members, because audiences run from hundreds to millions."
)

plot_df = view.copy()
plot_df["segment"] = "standard"
plot_df.loc[anchor_mask, "segment"] = "anchor"
plot_df.loc[traffic_mask, "segment"] = "traffic"

segment_colors = alt.Scale(
    domain=["standard", "anchor", "traffic"],
    range=["#9aa5b1", "#1f77b4", "#d62728"],
)

x_domain = [max(100, view["members"].min() * 0.8), view["members"].max() * 1.3]

points = (
    alt.Chart(plot_df)
    .mark_circle(size=34, opacity=0.55, stroke=None)
    .encode(
        x=alt.X("members:Q", scale=alt.Scale(type="log", domain=x_domain),
                title="Audience (MAL members, log scale)"),
        y=alt.Y("score:Q", scale=alt.Scale(zero=False), title="User score (0-10)"),
        color=alt.Color("segment:N", scale=segment_colors,
                        legend=alt.Legend(title="Segment", orient="top")),
        tooltip=[
            alt.Tooltip("title:N", title="Title"),
            alt.Tooltip("type_group:N", title="Type"),
            alt.Tooltip("year:Q", title="Year", format=".0f"),
            alt.Tooltip("score:Q", title="Score", format=".2f"),
            alt.Tooltip("members:Q", title="Members", format=","),
            alt.Tooltip("favorites:Q", title="Favourites", format=","),
            alt.Tooltip("studio:N", title="Studio"),
        ],
    )
)

vrule = (
    alt.Chart(pd.DataFrame({"x": [ANCHOR_REACH]}))
    .mark_rule(color="#444", strokeDash=[4, 4])
    .encode(x=alt.X("x:Q", scale=alt.Scale(type="log")))
)
hrule = (
    alt.Chart(pd.DataFrame({"y": [ANCHOR_SCORE]}))
    .mark_rule(color="#444", strokeDash=[4, 4])
    .encode(y=alt.Y("y:Q"))
)

hero = (
    (vrule + hrule + points)
    .properties(height=430)
    .resolve_scale(x="independent", y="independent")
)
st.altair_chart(hero, width="stretch")

if anchor_mask.any() or traffic_mask.any():
    busiest = (plot_df[plot_df["segment"].ne("standard")]
               .nlargest(3, "members")[["title", "segment", "score", "members"]])
    line = ", ".join(
        "**{t}** ({s}, {sc:.2f}, {m:,.0f} members)".format(
            t=row["title"], s=row["segment"], sc=row["score"], m=row["members"])
        for _, row in busiest.iterrows()
    )
    st.caption(f"The biggest audiences in the two decision corners right now: {line}.")

# ---------------------------------------------------------------- supporting charts

st.subheader("Which format and which genre earn their slot")
left, right = st.columns([1, 1])

type_stats = (
    view.groupby("type_group")
    .agg(titles=("score", "size"), median_score=("score", "median"),
         median_members=("members", "median"))
    .reset_index()
    .sort_values("median_score", ascending=False)
    .round(2)
)
with left:
    bars = (
        alt.Chart(type_stats)
        .mark_bar()
        .encode(
            x=alt.X("median_score:Q", title="Median score", scale=alt.Scale(domain=[0, 8])),
            y=alt.Y("type_group:N", sort="-x", title=None),
            color=alt.value("#1f77b4"),
            tooltip=[alt.Tooltip("type_group:N", title="Type"),
                     alt.Tooltip("titles:Q", title="Titles", format=","),
                     alt.Tooltip("median_score:Q", title="Median score", format=".2f"),
                     alt.Tooltip("median_members:Q", title="Median members", format=",")],
        )
        .properties(height=250, title="Median score by format")
    )
    st.altair_chart(bars, width="stretch")

with right:
    genre_df = view.assign(genre=view["genres"].str.split(",")).explode("genre")
    genre_df["genre"] = genre_df["genre"].str.strip()
    genre_df = genre_df[genre_df["genre"].ne("")]
    genre_stats = (
        genre_df.groupby("genre")
        .agg(titles=("score", "size"), median_score=("score", "median"),
             median_members=("members", "median"))
        .reset_index()
    )
    genre_stats = genre_stats[genre_stats["titles"] >= 20].sort_values(
        "median_score", ascending=False).head(10).round(2)
    if genre_stats.empty:
        st.info("Not enough titles per genre in this selection to rank genres.")
    else:
        gbars = (
            alt.Chart(genre_stats)
            .mark_bar()
            .encode(
                x=alt.X("median_score:Q", title="Median score", scale=alt.Scale(domain=[0, 8])),
                y=alt.Y("genre:N", sort="-x", title=None),
                color=alt.value("#2ca02c"),
                tooltip=[alt.Tooltip("genre:N", title="Genre"),
                         alt.Tooltip("titles:Q", title="Titles", format=","),
                         alt.Tooltip("median_score:Q", title="Median score", format=".2f"),
                         alt.Tooltip("median_members:Q", title="Median members", format=",")],
            )
            .properties(height=250, title="Top 10 genres by median score (20+ titles)")
        )
        st.altair_chart(gbars, width="stretch")

# ---------------------------------------------------------------- studio view

st.subheader("Which studios deserve a batch deal")
st.caption(
    "Median score of a studio's titles, once the studio has at least the number of titles you "
    "choose. Raise it to keep only studios with a real track record."
)
min_studio_titles = st.slider("Minimum titles from a studio", 5, 50, 10, step=5)

studio_df = view[view["studio"].ne("UNKNOWN")]
studio_stats = (
    studio_df.groupby("studio")
    .agg(titles=("score", "size"), median_score=("score", "median"),
         median_members=("members", "median"),
         anchor_titles=("score", lambda s: int((s >= ANCHOR_SCORE).sum())))
    .reset_index()
)
studio_stats = studio_stats[studio_stats["titles"] >= min_studio_titles]
studio_stats = studio_stats.sort_values(
    ["median_score", "titles"], ascending=[False, False]).round(2)

if studio_stats.empty:
    st.info("No studio has that many titles in this selection.")
else:
    st.dataframe(
        studio_stats,
        width="stretch",
        hide_index=True,
        column_config={
            "studio": "Studio",
            "titles": st.column_config.NumberColumn("Titles"),
            "median_score": st.column_config.NumberColumn("Median score", format="%.2f"),
            "median_members": st.column_config.NumberColumn("Median members", format="%d"),
            "anchor_titles": st.column_config.NumberColumn("Anchor titles"),
        },
        height=320,
    )
    st.caption(
        f"{len(studio_df):,} of the {n_titles:,} titles in this selection credit a named studio; "
        f"the other {n_titles - len(studio_df):,} are listed as **UNKNOWN**, which the source "
        "data does not let us fix."
    )

# ---------------------------------------------------------------- detail table

with st.expander("Detail: the shortlist behind the numbers"):
    pick = st.radio("Show", ["Anchor candidates", "Traffic-only titles", "All titles"],
                    horizontal=True, label_visibility="collapsed")
    if pick == "Anchor candidates":
        table = view.loc[anchor_mask]
    elif pick == "Traffic-only titles":
        table = view.loc[traffic_mask]
    else:
        table = view
    table = table.sort_values("members", ascending=False)[
        ["title", "type_group", "year", "score", "members", "favorites", "studio"]
    ]
    st.dataframe(table, width="stretch", hide_index=True, height=340)
    st.download_button(
        "Download this list as CSV",
        data=table.to_csv(index=False).encode("utf-8"),
        file_name="anistream_shortlist.csv",
        mime="text/csv",
    )

# ---------------------------------------------------------------- data period and caveats

st.divider()
st.caption(
    f"**{DATA_PERIOD}** — {len(raw):,} scored, finished titles with a known first-airing year "
    "(65.5% of the 30,763 rows in the Kaggle snapshot; the rest were never scored by users). "
    "Scores are MAL user ratings, not AniStream viewing data: they are a proxy for reception, "
    "and the audience counts are lifetime MAL members, not monthly streams. "
    "**Studio = UNKNOWN** for 39% of the source rows, so studio comparisons describe only the "
    "credited titles."
)
