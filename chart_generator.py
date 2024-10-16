import streamlit as st
import pandas as pd
from matplotlib.image import imread

import yaml
import os
import math

import chart

def map(number, inMin, inMax, outMin, outMax):
    return (number - inMin) * (outMax - outMin) / (inMax - inMin) + outMin

def load_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def save_config(config, file_path):
    with open(file_path, 'w') as file:
        yaml.dump(config, file, default_flow_style=False)

config_file_path = 'config.yaml'

# Load the current configuration
if os.path.exists(config_file_path):
    config = load_config(config_file_path)
else:
    config = {
        'resolutions': ['3840x2160', '1920x1080', '1300x1300'], 
        'default_colours': ['#f0991a', '#820000', '#32f01a', '#af1af0', '#016795'], 
        'title_presets': ['CPU Scores', 'GPU Scores'], 
        'sub_title_presets': ['Higher scores indicate higher performance', 'Lower scores indicate higher performance']
        }
    save_config(config, config_file_path)


st.set_page_config(
    page_title="Chart Generator",
    initial_sidebar_state='collapsed'
)   


st.title("Chart Generator")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)


    preview = st.checkbox("Show Preview")
    if preview:
        st.subheader("Data Preview")
        st.write(df.head())

    # Number of colors calc
    score_cols = df.columns.str.startswith('score_').sum()
    col1, col2 = st.columns(2)

    # Title
    title_custom = col1.text_input("Chart Title")

    title_dropdown_disabled = bool(title_custom)

    title_dd = col1.selectbox(
                    "Title Presets", 
                    config["title_presets"]
                    ,disabled=title_dropdown_disabled
                )
    
    if title_dropdown_disabled:
        title = title_custom
    else:
        title = title_dd


    # Sub Text
    sub_text_custom = col1.text_input("Sub Text")

    st_dropdown_disabled = bool(sub_text_custom)

    sub_text_dd = col1.selectbox(
                    "Sub Text Presets", 
                    config["sub_title_presets"]
                    ,disabled=st_dropdown_disabled
                )
    
    if st_dropdown_disabled:
        sub_text = sub_text_custom
    else:
        sub_text = sub_text_dd



    #Bar thickness
    if score_cols == 1:
        bar_width = col2.slider("Bar Thickness", min_value=0.1, value=0.5, step=0.05)
    elif score_cols == 2:
        bar_width = col2.slider("Bar Thickness", min_value=0.1, value=0.4, step=0.05)
    elif score_cols == 3:
        bar_width = col2.slider("Bar Thickness", min_value=0.1, value=0.2, step=0.05)
    elif score_cols == 4:
        bar_width = col2.slider("Bar Thickness", min_value=0.1, value=0.1, step=0.05)

    #Font Size
    if 'subheading' in df:
        longest_string = max(df["heading"].str.len().max(), df["subheading"].str.len().max())
    else:
        longest_string = df["heading"].str.len().max()

    tick_default_size = math.floor(map(longest_string, 1, 30, 30, 5))

    title_font_size = col2.slider("Title Font Size", min_value=10, max_value=50, value=30, step=1)
    subtitle_font_size = col2.slider("Sub Title Font Size", min_value=5, max_value=50, value=15, step=1)
    axis_font_size = col2.slider("Axis Font Size", min_value=5, max_value=30, value=tick_default_size, step=1)
    legend_font_size = col2.slider("Legend Font Size", min_value=5, max_value=30, value=25, step=1)
    bar_data_font_size = col2.slider("Bar Data Font Size", min_value=5, max_value=30, value=15, step=1)


    # Margin Size
    x_title_pos = col2.slider("X Title Pos", min_value=0.1, max_value=1.0, value=0.0, step=0.01)
    y_title_pos = col2.slider("Y Title Pos", min_value=0.0, max_value=1.1, value=1.05, step=0.01)

    # Bar Score Position
    bar_score_offset = col2.slider("Bar Score Position", min_value=0, max_value=200, value=110, step=1)

    # Size Selector
    size = col1.selectbox("Chart Size", config['resolutions'])

    # Sorted Selector
    cols = list(df.columns.values)
    cols.insert(0, "None")
    sorted_col = col1.selectbox("Sorted By", cols)
    is_ascending = col1.toggle("Ascending?")

    # Highlight Selector
    unique_values = df['heading'].unique()
    unique_values = list(unique_values)
    unique_values.insert(0, "None")
    highlight_col = col1.selectbox("Highlight Column", unique_values)
    highlight_color_disabled = False
    if highlight_col == "None":
        highlight_color_disabled = True
    

    col_col1, col_col2, col_col3, col_col4 = st.columns(4)
    colours = {}
    legend = {}
    default_cols = config["default_colours"]
    col_index = 0
    for i, column in enumerate(df.columns):
        if df[column].name.startswith("score_"):
        # st.color_picker("Bar " + str(i+1) + " Colour")
            colours["col"+str(i)] = eval("col_col"+str(i)).color_picker(df.columns.tolist()[i]+" Colour", default_cols[col_index])
            legend["col"+str(i)] = eval("col_col"+str(i)).text_input(df.columns.tolist()[i] + " Legend Text", df.columns.tolist()[i].split("_")[1])
            col_index = col_index + 1


    bg_color = st.color_picker("Background Colour", default_cols[4], disabled=highlight_color_disabled)
    highlight_color = st.color_picker("Highlight Colour", default_cols[5], disabled=highlight_color_disabled)


    filename = 'output.png'
    if st.button("Generate Chart"):
        chart.generate_chart(df, 
                            filename, 
                            size, 
                            bg_color, 
                            sorted_col, 
                            is_ascending, 
                            highlight_col, 
                            colours, 
                            highlight_color, 
                            bar_width, 
                            bar_score_offset, 
                            title_font_size, 
                            subtitle_font_size,
                            axis_font_size, 
                            legend_font_size,
                            bar_data_font_size,
                            title, 
                            x_title_pos, 
                            y_title_pos, 
                            sub_text, 
                            legend
                            )
        image = imread(filename)
        st.image(image)
        with open(filename, "rb") as file:
            btn = st.download_button(
                label="Download chart",
                data=file,
                file_name=title,
                mime="image/png",
            )
else:
    st.write("Waiting on file upload...")

    