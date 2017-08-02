import csv
import pandas as pd
import numpy as np
import os
import pickle
import gmplot
from selenium import webdriver
import sys
import time
from PIL import Image
try:
    from us_polygon_mapper.defaults import defaults
    from us_polygon_mapper.us_state_abbrev import us_state_abbrev
    from us_polygon_mapper.color_rgb_dict import color_rgb_dict
except:
    from defaults import defaults
    from us_state_abbrev import us_state_abbrev
    from color_rgb_dict import color_rgb_dict

def csv_to_values_dict(csv_path, columns=None):
    if not csv_path.endswith(".csv"):
        csv_path += ".csv"

    with open(csv_path, "r") as csv_file:
        csv_reader = csv.reader(csv_file)

        # creating dictionary {state: value}
        values_dict = {}

        col_nums = {'state': 0, 'value': 1}

        for row_idx, line in enumerate(csv_reader):
            # check for column names:
            if ((row_idx == 0) and (columns is not None)):
                try:
                    col_nums['state'] = int(columns[0])
                    col_nums['value'] = int(columns[1])
                except:
                    col_nums = {'state': None, 'value': None}
                    for col_idx, element in enumerate(line):
                        if element.lower() == columns[0].lower():
                            col_nums['state'] = col_idx
                        elif element.lower() == columns[1].lower():
                            col_nums['value'] = col_idx
                        if None not in col_nums.values():
                            break
                if None in col_nums.values():
                    raise Exception("Invalid columns entered.")

            # abbreviated
            if line[col_nums['state']].upper() in us_state_abbrev.values():
                values_dict[line[col_nums['state']].upper()
                    ] = float(line[col_nums['value']])
            # full name
            elif line[col_nums['state']].title() in us_state_abbrev.keys():
                values_dict[us_state_abbrev[line[col_nums['state']
                    ].title()]] = float(line[col_nums['value']])

    return values_dict

def num_to_hex(num):
    return hex(int(num))[2:].zfill(2)

def value_to_color(
    value, lo, hi, low_color=defaults['low_color'],
    high_color=defaults['high_color']):
    color = "#"
    try:
        normalized = (value - lo) / (hi - lo)
    except ZeroDivisionError:
        normalized = 0.5
    for i in range(len(low_color)):
        distance = high_color[i] - low_color[i]
        color += num_to_hex(low_color[i] + (distance * normalized))

    return color

def make_state_colors_dict(
    values_dict, low_color=defaults['low_color'],
    high_color=defaults['high_color'], middle=defaults['middle']):
    all_values = list(values_dict.values())

    # parse middle argument
    try:
        middle = float(middle)
    except:
        if middle in ["mean", "average"]:
            middle = np.mean(all_values)
        elif middle == "median":
            middle = np.median(all_values)
        elif middle.startswith("percentile"):
            try:
                pct = float(middle.split('=')[1])
            except:
                raise Exception(("Invalid percentile entered. "
                        "Use syntax: 'percentile=75'."))
            if 0 <= pct <= 100:
                middle = np.percentile(all_values, pct)
            else:
                raise Exception("Percentile must be between 0 and 100")
        else:
            raise Exception(("Invalid middle entered. Options are: "
                    "'median', 'mean', a number, or 'percentile=x'."))

    # converting names of colors to RGB tuples
    try:
        light_low_color = color_rgb_dict["light_" + low_color]
        low_color = color_rgb_dict[low_color]

        light_high_color = color_rgb_dict["light_" + high_color]
        high_color = color_rgb_dict[high_color]
    except:
        raise Exception(("Invalid color entered. Options are: red, orange, "
                "yellow, green, blue, purple, brown."))

    low_values_dict = {}
    high_values_dict = {}
    for key, value in values_dict.items():
        if value <= middle:
            low_values_dict[key] = value
        else:
            high_values_dict[key] = value

    low_values = low_values_dict.values()
    if len(low_values) > 0:
        low_lo = min(low_values)
        low_hi = max(low_values)
        low_colors_dict = {
            key: value_to_color(
                value, low_lo, low_hi,
                low_color, light_low_color)
            for key, value in low_values_dict.items()
        }
    else:
        low_colors_dict = {}

    high_values = high_values_dict.values()
    if len(high_values) > 0:
        high_lo = min(high_values)
        high_hi = max(high_values)
        high_colors_dict = {
            key: value_to_color(
                value, high_lo, high_hi, light_high_color, high_color)
            for key, value in high_values_dict.items()
        }
    else:
        high_colors_dict = {}

    state_colors_dict = {
        key: value
        for d in [low_colors_dict, high_colors_dict]
        for key, value in d.items()
    }

    return state_colors_dict

def plot_states(state_colors_dict, html_fn=defaults['html_fn']):
    # loading state polygon_dict
    with open(os.path.join(os.path.dirname(__file__),
            'state_polygon_dict.pickle'), 'rb') as handle:
        state_polygon_dict = pickle.load(handle)

    gmap = gmplot.GoogleMapPlotter(39.50, -98.35, 5)

    for key, value in state_polygon_dict.items():
        # state in data
        if key in state_colors_dict.keys():
            gmap.polygon(
                value['lats'], value['lngs'],
                color=state_colors_dict[key], face_alpha=0.7)
        # state not in data
        else:
            gmap.polygon(
                value['lats'], value['lngs'],
                color='#000000', face_alpha=0.3)

    if not html_fn.endswith(".html"):
        html_fn += ".html"

    gmap.draw(html_fn)

    return html_fn

def screenshot_html(html_fn, png_fn=defaults['png_fn']):
    # starting browser
    driver = webdriver.PhantomJS(service_log_path='ghostdriver.log')
    driver.set_window_size(1750, 1000)

    # Windows file:///, Other file://
    if sys.platform.startswith('win'):
        url_beginning = "file:///"
    else:
        url_beginning = "file://"

    if not png_fn.endswith(".png"):
        png_fn += ".png"

    driver.get(
        url_beginning + (os.getcwd() + '/' + html_fn).replace(' ', '%20')
        .replace('\\', '/'))

    # waiting to let browser finish loading
    time.sleep(5)

    driver.save_screenshot(png_fn)
    driver.quit()

    # deleting automatically generated log file
    try:
        os.remove('ghostdriver.log')
    except:
        pass

    # crop image
    img = Image.open(png_fn)
    img = img.crop((125, 100, 1650, 971))
    img.save(png_fn)

    return png_fn

# Functions for users

# html
def dict_to_html(
        values_dict, low_color=defaults['low_color'],
        high_color=defaults['high_color'], middle=defaults['middle'],
        html_fn=defaults['html_fn']):
    state_colors_dict = make_state_colors_dict(
        values_dict, low_color, high_color, middle)
    html_fn = plot_states(state_colors_dict, html_fn)
    return html_fn

def csv_to_html(
        csv_path, low_color=defaults['low_color'],
        high_color=defaults['high_color'], middle=defaults['middle'],
        columns=None, html_fn=defaults['html_fn']):
    values_dict = csv_to_values_dict(csv_path, columns)
    html_fn = dict_to_html(
        values_dict, low_color, high_color, middle, html_fn)
    return html_fn

def df_to_html(
        df, low_color=defaults['low_color'],
        high_color=defaults['high_color'], middle=defaults['middle'],
        columns=None, html_fn=defaults['html_fn']):
    csv_path = "df_to_csv.csv"
    df.to_csv(csv_path)
    html_fn = csv_to_html(
        csv_path, low_color, high_color, middle, columns, html_fn)
    os.remove(csv_path)
    return html_fn

# png
def dict_to_png(
        values_dict, low_color=defaults['low_color'],
        high_color=defaults['high_color'], middle=defaults['middle'],
        png_fn=defaults['png_fn'], html_fn=defaults['html_fn']):
    html_fn = dict_to_html(
        values_dict, low_color, high_color, middle, html_fn)
    png_fn = screenshot_html(html_fn, png_fn)
    return png_fn

def csv_to_png(
        csv_path, low_color=defaults['low_color'],
        high_color=defaults['high_color'], middle=defaults['middle'],
        columns=None, png_fn=defaults['png_fn'], html_fn=defaults['html_fn']):
    html_fn = csv_to_html(
        csv_path, low_color, high_color, middle, columns, html_fn)
    png_fn = screenshot_html(html_fn, png_fn)
    return png_fn

def df_to_png(
        df, low_color=defaults['low_color'],
        high_color=defaults['high_color'], middle=defaults['middle'],
        columns=None, png_fn=defaults['png_fn'], html_fn=defaults['html_fn']):
    html_fn = df_to_html(df, low_color, high_color, middle, columns, html_fn)
    png_fn = screenshot_html(html_fn, png_fn)
    return png_fn