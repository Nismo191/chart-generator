# libraries
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Rectangle
import numpy as np
import pandas as pd
import textwrap

def gradientbars(bars, range, colmap):
      
      ax = bars[0].axes
      lim = ax.get_xlim()+ax.get_ylim()
      for bar in bars:
          bar.set_zorder(1)
          bar.set_facecolor("none")
          x,y = bar.get_xy()
          w, h = bar.get_width(), bar.get_height()
          grad = np.atleast_2d(np.linspace(0,1*w/w,256))
          ax.imshow(grad, extent=[x,x+w,y,y+h], aspect="auto", zorder=0, norm=mcolors.NoNorm(vmin=0,vmax=1), cmap=colmap)
      ax.axis(lim)  

def hex_to_rgb(hex):
  hex = hex.replace("#", "")
  rgb = []
  for i in (0, 2, 4):
    decimal = int(hex[i:i+2], 16)
    rgb.append(decimal/255)
  
  return tuple(rgb)

def adjust_brightness(color, factor):
    return tuple(min(1, max(0, c * factor)) for c in color)



def get_colors(colours):
    cmaps = []
    for key, value in colours.items():
        col1_1 = adjust_brightness(value, 1.2)
        col1_2 = adjust_brightness(value, 0.8)
        
        # Define colors to use in the colormap
        colors1 = [col1_1, col1_2] 

        # Create a custom colormap
        cmap_name = key
        cmaps.append(mcolors.LinearSegmentedColormap.from_list(cmap_name, colors1, N=256))

    return cmaps


def generate_chart(df, size, bg_color, sorted_col, is_ascending, highlight, colours, highlight_color, bar_width, bar_score_offset, title_font_size, tick_font_size, title, left_margin_size, right_margin_size, sub_text, legend_text):
    x_tick_font_size = 15
    if size == "3840x2160":
        title_font_size = title_font_size*2
        tick_font_size = tick_font_size*2
        x_tick_font_size = x_tick_font_size*2
        

   
    col_keys = []

    for key, value in colours.items():
        col_keys.append(key)
        colours[key] = hex_to_rgb(colours[key])

    colours["highlight"] = hex_to_rgb(highlight_color)
    custom_cmaps = get_colors(colours)

    # Sort DF
    if sorted_col != "None":
        df = df.sort_values(by=[sorted_col], ascending=is_ascending)



    # Set Plot size
    size = size.split("x")
    px = 1/plt.rcParams['figure.dpi']
    fig, ax = plt.subplots(figsize=(int(size[0])*px,int(size[1])*px))



    # # Change background colors
    fig.patch.set_facecolor(bg_color) 
    ax.set_facecolor(bg_color)   

    # # Change font color
    ax.tick_params(axis='y', colors='white', width=2)  # Y-axis tick labels
    ax.tick_params(axis='x', colors='white', width=2)  # X-axis tick labels
    title = ax.set_title(title, fontsize = title_font_size, color='white', bbox=dict(facecolor='#005CB9', edgecolor='black', boxstyle='square,pad=0.2'), loc='left')

    if sub_text != "":
        wrapped_text = "\n".join(textwrap.wrap(sub_text, width=25))
        ax.text(0.95, 1.02, wrapped_text, transform=ax.transAxes, color='white',fontsize=tick_font_size, verticalalignment='center', horizontalalignment='right', bbox=dict(facecolor='#005CB9',boxstyle='square,pad=0.5'))


    # Set the positions for the bars
    positions = np.arange(len(df['heading']))
    bars = []

    # Create Bars
    for i, column in enumerate(df.columns):
        if df[column].name.startswith("score_"):
            bars.append(ax.barh(positions + (i - len(df.columns)/2) * bar_width, df[column], bar_width, color='xkcd:red', edgecolor='xkcd:red'))

    # Apply Gradients to bars
    for i, bar in enumerate(bars):
        gradientbars(bar, 3000, custom_cmaps[i])
        ax.bar_label(bar, padding=-bar_score_offset, color='white', fontsize=tick_font_size-2, label_type='edge', fontweight='bold')
        


    if highlight != "None":
        for i, bar_group in enumerate(bars):
            for bar, labal in zip(bar_group, df['heading']):
                if labal == highlight:
                    # bar.set_color(highlight_color)

                    # Little bit hacky, gradientbars function take an array of bars
                    bar.set_zorder(1)
                    bar.set_facecolor("none")
                    x,y = bar.get_xy()
                    w, h = bar.get_width(), bar.get_height()
                    grad = np.atleast_2d(np.linspace(0,1*w/w,256))
                    ax.imshow(grad, extent=[x,x+w,y,y+h], aspect="auto", zorder=0, norm=mcolors.NoNorm(vmin=0,vmax=1), cmap=custom_cmaps[len(custom_cmaps)-1])

                    bar.set_edgecolor(colours[col_keys[i]])
                    bar.set_linewidth(2)
        


    ax.spines[['right', 'top']].set_visible(False)

    ax.spines[['left', 'bottom']].set_color("White")
    ax.spines[['left', 'bottom']].set_linewidth(2.5)
    ax.spines[['left', 'bottom']].set(joinstyle="bevel")


    if 'subheading' in df:
        # # Set the y-ticks to be the positions and labels
        y_labels = [f"{heading}\n{subheading}" for heading, subheading in zip(df['heading'], df['subheading'])]
    else:
        # # Set the y-ticks to be the positions and labels
        y_labels = [f"{heading}" for heading in df['heading']]



    positions = positions.astype('float64')
    
    # Apply offset
    for i, pos in enumerate(positions):
        positions[i] = float(positions[i]) - 0.2

    ax.set_yticks(positions)
    ax.set_yticklabels(y_labels, ha='right')

    plt.subplots_adjust(left=left_margin_size, right=right_margin_size)

    plt.yticks(fontsize=tick_font_size)
    plt.xticks(fontsize=x_tick_font_size)


    legend = []
    col_index = 0

    for i, column in enumerate(df.columns):
        if df[column].name.startswith("score_"):
            legend.append(Rectangle((0, 0), 20, 20, fc=colours[col_keys[col_index]], edgecolor='black', label=legend_text["col"+str(col_index+1)]))
            col_index = col_index + 1


    ax.legend(bbox_to_anchor=(-0.05, 0), handles=legend, fontsize=tick_font_size/2, handlelength=2.5, handleheight=2, borderaxespad=0.5)

    # plt.show()
    plt.savefig("frameview_output.png")

    return df








