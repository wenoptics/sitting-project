import io
from multiprocessing import Process
from threading import Thread

import requests
import pandas as pd
from bokeh.application import Application
from bokeh.application.handlers import FunctionHandler
from bokeh.models import ColumnDataSource, HoverTool, SaveTool, WheelZoomTool, PanTool, ResetTool
from bokeh.models.widgets import TextInput, Button
from bokeh.plotting import figure, curdoc
from bokeh.layouts import row, widgetbox, column
import numpy as np
from bokeh.server.server import Server
from tornado.ioloop import IOLoop

current_time = 0


def make_document(doc):
    base = "http://192.168.50.62/get?gyrX=%s|gyr_time&gyr_time=%s&gyrY=%s|gyr_time&gyrZ=%s|gyr_time"
    data = ColumnDataSource(dict(
        time=[],
        # display_time=[],
        x=[],
        y=[],
        z=[],
    ))

    def get_last():
        global current_time
        # print(current_time)

        raw = requests.get(base % (current_time, current_time, current_time, current_time))
        j = raw.json()

        ln = min(
            len(j['buffer']["gyr_time"]["buffer"]),
            len(j['buffer']["gyrX"]["buffer"]),
            len(j['buffer']["gyrY"]["buffer"]),
            len(j['buffer']["gyrZ"]["buffer"]),
        )

        prices_df = pd.DataFrame.from_dict({"time": j['buffer']["gyr_time"]["buffer"][:ln],
                                            "x": j['buffer']["gyrX"]["buffer"][:ln],
                                            "y": j['buffer']["gyrY"]["buffer"][:ln],
                                            "z": j['buffer']["gyrZ"]["buffer"][:ln],
                                            })

        if len(j['buffer']["gyr_time"]["buffer"]) == 0:
            current_time = 0
        else:
            current_time = j['buffer']["gyr_time"]["buffer"][-1]

        # prices_df["time"] = pd.to_datetime(prices_df["time"], unit="ms")
        # prices_df["display_time"] = prices_df["time"].dt.strftime("%m-%d-%Y %H:%M:%S.%f")

        return prices_df

    def update_price():

        new_price = get_last()
        print(len(new_price['time']), end='\n\n')
        data.stream(
            dict(time=new_price["time"],
                 x=new_price["x"],
                 y=new_price["y"],
                 z=new_price["z"]
                 ),
            1000)
        return

    hover = HoverTool(tooltips=[
        ("Time", "@display_time"),
        ("IEX Real-Time Price", "@price")
    ])

    fig_x = figure(plot_width=800,
                        plot_height=400,
                        x_axis_type='datetime',
                        tools=[WheelZoomTool(), ResetTool(), PanTool(), SaveTool()],
                        title="Real-Time Price Plot")

    fig_x.line(source=data, color="navy", x='time', y='x')
    fig_x.xaxis.axis_label = "Time"
    fig_x.yaxis.axis_label = "IEX Real-Time Price"
    fig_x.title.text = "IEX Real Time Price: "

    fig_y = figure(plot_width=800,
                        plot_height=400,
                        x_axis_type='datetime',
                        tools=[WheelZoomTool(), ResetTool(), PanTool(), SaveTool()],
                        title="Real-Time Price Plot",
                   x_range=fig_x.x_range, y_range=fig_x.y_range)

    fig_y.line(source=data, color="navy", x='time', y='y')
    fig_y.xaxis.axis_label = "Time"
    fig_y.yaxis.axis_label = "IEX Real-Time Price"
    fig_y.title.text = "IEX Real Time Price: "


    fig_z = figure(plot_width=800,
                        plot_height=400,
                        x_axis_type='datetime',
                        tools=[WheelZoomTool(), ResetTool(), PanTool(), SaveTool()],
                        title="Real-Time Price Plot",
                   x_range=fig_x.x_range, y_range=fig_x.y_range)

    fig_z.line(source=data, color="navy", x='time', y='z')
    fig_z.xaxis.axis_label = "Time"
    fig_z.yaxis.axis_label = "IEX Real-Time Price"
    fig_z.title.text = "IEX Real Time Price: "

    ticker_textbox = TextInput(placeholder="Ticker")
    update = Button(label="Update")

    inputs = widgetbox([ticker_textbox, update], width=200)

    doc.add_root(column(fig_x, fig_y, fig_z, width=1600))
    doc.title = "Real-Time Price Plot from IEX"
    doc.add_periodic_callback(update_price, 30)


apps = {'/': Application(FunctionHandler(make_document))}

server = Server(apps, port=5006)
server.start()

IOLoop.current().start()
