import io
from multiprocessing import Process
from threading import Thread

import requests
import pandas as pd
from bokeh.application import Application
from bokeh.application.handlers import FunctionHandler
from bokeh.models import ColumnDataSource, HoverTool, SaveTool, WheelZoomTool, PanTool, ResetTool, Div
from bokeh.models.widgets import TextInput, Button
from bokeh.plotting import figure, curdoc
from bokeh.layouts import row, widgetbox, column
import numpy as np
from bokeh.server.server import Server
from tornado.ioloop import IOLoop

current_time = 0

current_accg = np.array([0,0,0])
reset_accg = np.array([0.33335678,9.49056427,-2.60099121])


def calc_angle_dev(current_accg):
    global reset_accg
    a, b = current_accg, reset_accg

    # print(current_accg.shape)
    if len(current_accg.shape) == 1 or current_accg.shape[1] == 0:
        return np.nan

    return np.arccos(
        a.dot(b.T) / (np.linalg.norm(a, axis=1) * np.linalg.norm(b))
    ) * 180 / np.pi


def make_document(doc):
    TICKER = ""
    base = "http://192.168.50.62/get?accX=%s|acc_time&acc_time=%s&accY=%s|acc_time&accZ=%s|acc_time"
    data = ColumnDataSource(dict(
        time=[],
        # display_time=[],
        x=[],
        y=[],
        z=[],
        angle_dev=[]

    ))

    def get_last():
        global current_time
        global current_accg
        # print(current_time)

        raw = requests.get(base % (current_time, current_time, current_time, current_time))
        j = raw.json()

        ln = min(
            len(j['buffer']["acc_time"]["buffer"]),
            len(j['buffer']["accX"]["buffer"]),
            len(j['buffer']["accY"]["buffer"]),
            len(j['buffer']["accZ"]["buffer"]),
        )

        prices_df = pd.DataFrame.from_dict({"time": j['buffer']["acc_time"]["buffer"][:ln],
                                            "x": j['buffer']["accX"]["buffer"][:ln],
                                            "y": j['buffer']["accY"]["buffer"][:ln],
                                            "z": j['buffer']["accZ"]["buffer"][:ln],
                                            "angle_dev": calc_angle_dev(
                                                np.array(
                                                    [
                                                        j['buffer']["accX"]["buffer"][:ln],
                                                        j['buffer']["accY"]["buffer"][:ln],
                                                        j['buffer']["accZ"]["buffer"][:ln],
                                                    ]
                                                ).T
                                            ),
                                            })

        if len(j['buffer']["acc_time"]["buffer"]) == 0:
            current_time = 0
        else:
            current_time = j['buffer']["acc_time"]["buffer"][-1]


        current_accg = np.array([[
            j['buffer']["accX"]["buffer"][-1],
            j['buffer']["accY"]["buffer"][-1],
            j['buffer']["accZ"]["buffer"][-1]]]
        )

        div.text = f'angle is: {calc_angle_dev(current_accg)} ' \
                   f'<br>' \
                   f'current_accg is {current_accg}'

        # prices_df["time"] = pd.to_datetime(prices_df["time"], unit="ms")
        # prices_df["display_time"] = prices_df["time"].dt.strftime("%m-%d-%Y %H:%M:%S.%f")

        return prices_df

    def update_price():

        new_price = get_last()
        # print(len(new_price['time']), end='\n\n')
        data.stream(
            dict(time=new_price["time"],
                 x=new_price["x"],
                 y=new_price["y"],
                 z=new_price["z"],
                 angle_dev=new_price["angle_dev"]
                 ),
            1000)
        return

    hover = HoverTool(tooltips=[
        ("Time", "@display_time"),
        ("IEX Real-Time Price", "@price")
    ])

    fig_x = figure(plot_width=800,
                        plot_height=300,
                        x_axis_type='datetime',
                        tools=[WheelZoomTool(), ResetTool(), PanTool(), SaveTool()],
                        title="Real-Time Price Plot")

    fig_x.line(source=data, color="navy", x='time', y='x')
    fig_x.xaxis.axis_label = "Time"
    fig_x.yaxis.axis_label = "IEX Real-Time Price"
    fig_x.title.text = "IEX Real Time Price: " + TICKER

    fig_y = figure(plot_width=800,
                        plot_height=300,
                        x_axis_type='datetime',
                        tools=[WheelZoomTool(), ResetTool(), PanTool(), SaveTool()],
                        title="Real-Time Price Plot",
                   x_range=fig_x.x_range, y_range=fig_x.y_range)

    fig_y.line(source=data, color="navy", x='time', y='y')
    fig_y.xaxis.axis_label = "Time"
    fig_y.yaxis.axis_label = "IEX Real-Time Price"
    fig_y.title.text = "IEX Real Time Price: " + TICKER


    fig_z = figure(plot_width=800,
                        plot_height=300,
                        x_axis_type='datetime',
                        tools=[WheelZoomTool(), ResetTool(), PanTool(), SaveTool()],
                        title="Real-Time Price Plot",
                   x_range=fig_x.x_range, y_range=fig_x.y_range)

    fig_z.line(source=data, color="navy", x='time', y='z')
    fig_z.xaxis.axis_label = "Time"
    fig_z.yaxis.axis_label = "IEX Real-Time Price"
    fig_z.title.text = "IEX Real Time Price: " + TICKER

    fig_angle_dev = figure(plot_width=800,
                   plot_height=300,
                   x_axis_type='datetime',
                   tools=[WheelZoomTool(), ResetTool(), PanTool(), SaveTool()],
                   title="angle dev",
                   x_range=fig_x.x_range, y_range=fig_x.y_range)

    fig_angle_dev.line(source=data, color="navy", x='time', y='angle_dev')
    fig_angle_dev.xaxis.axis_label = "Time"
    fig_angle_dev.yaxis.axis_label = "IEX Real-Time Price"
    fig_angle_dev.title.text = "IEX Real Time Price: " + TICKER

    div = Div(text="""
    <p>???<p>
    """,width=200, height=100)

    def reset_sit():
        # global current_accg
        # global reset_accg
        # reset_accg = current_accg
        print('reset btn clicked', reset_accg)

    button = Button(label="Reset Sit", button_type="success")
    button.on_click(reset_sit)

    doc.add_root(column(fig_x, fig_y, fig_z, button, div, fig_angle_dev))
    doc.title = "Real-Time Price Plot from IEX"
    doc.add_periodic_callback(update_price, 30)


apps = {'/': Application(FunctionHandler(make_document))}

print('visit http://localhost:5006')
server = Server(apps, port=5006)
server.start()

IOLoop.current().start()
