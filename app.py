import streamlit as st
import pandas as pd
import pydeck as pdk

# ---------- НАСТРОЙКИ СТРАНИЦЫ ----------
st.set_page_config(page_title="80 лет Калининградской области", layout="wide")
st.title("Главные исторические события региона")
st.markdown("Интерактивная карта и таймлайн к юбилею области")

# ---------- ЗАГРУЗКА ДАННЫХ ----------
@st.cache_data
def load_data():
    df = pd.read_csv("data/events4.csv", encoding='UTF-8')
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    df = df.dropna(subset=["lat", "lon"])
    return df

df = load_data()

# ---------- ПОСТРОЕНИЕ ДВУХ КОЛОНОК ----------
col_left, col_right = st.columns([5, 2])

# ---------- ЛЕВАЯ КОЛОНКА: КАРТА, СЛАЙДЕРЫ ----------
with col_left:
    min_year = int(df["year"].min())
    max_year = int(df["year"].max())
    selected_year = st.slider(
        "Выберите диапазон:",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        step=1
    )
    start_year, end_year = selected_year
    map_height = st.slider(
        "Размер карты:",
        min_value=1,
        max_value=20,
        value=5,
        step=1
    )
    filtered_df = df[(df["year"] >= start_year) & (df["year"] <= end_year)]

    if filtered_df.empty:
        st.warning("Нет событий для выбранного года.")
        st.stop()
    # Слой с точками
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=filtered_df,
        get_position=["lon", "lat"],
        get_radius=300,
        get_fill_color=[200, 30, 30, 180],
        pickable=True,
        auto_highlight=True,
    )
    # Слой с текстовыми подписями
    text_layer = pdk.Layer(
        "TextLayer",
        data=filtered_df,
        get_position=["lon", "lat"],
        get_text="title",
        get_size=12,
        get_color=[255, 255, 255],
        get_angle=0,
        get_text_anchor="middle",
        get_alignment_baseline="top",
        get_pixel_offset=[0, 30],
        font_family="Arial",
        font_weight="bold",
    )
    view_state = pdk.ViewState(
        latitude=54.7,
        longitude=20.5,
        zoom=7,
        pitch=0,
    )
    st.pydeck_chart(
        pdk.Deck(
            layers=[scatter_layer, text_layer],
            initial_view_state=view_state,
            tooltip={
                "html": "<b>{title}</b><br/>{year} г.",
                "style": {"backgroundColor": "steelblue", "color": "white"}
            }
        ),
        height=map_height*100
    )


# ---------- ПРАВАЯ КОЛОНКА: ТАЙМЛАЙН ----------
with col_right:
    st.subheader(f"События с {start_year} по {end_year} год")
    for _, row in filtered_df.sort_values("year").iterrows():
        with st.expander(f"{row['year']} — {row['title']}"):
            st.write(f"**Описание:** {row['description']}")
            if "science_fact" in row and pd.notna(row['science_fact']):
                st.info(f"**Интересный факт:** {row['science_fact']}")
            if "photo_filename" in row and pd.notna(row['photo_filename']):
                try:
                    from PIL import Image
                    img = Image.open(f"assets/photos/{row['photo_filename']}")
                    st.image(img, caption=row['title'], width=300)
                except:
                    pass
                    #st.caption("Фото временно недоступно")
            st.caption(f"Источник: {row.get('source', '—')}")
