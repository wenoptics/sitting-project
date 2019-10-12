"""

"""

import requests
import pandas as pd
from bokeh.application import Application
from bokeh.application.handlers import FunctionHandler
from bokeh.models import ColumnDataSource, HoverTool, SaveTool, WheelZoomTool, PanTool, ResetTool, Div, BoxAnnotation
from bokeh.models.widgets import TextInput, Button
from bokeh.plotting import figure, curdoc
from bokeh.layouts import row, widgetbox, column
import numpy as np
from bokeh.server.server import Server
from tornado.ioloop import IOLoop


def make_document(doc):
    print(doc)

    # Create some random data
    x = np.random.random(2500) * 140 - 20
    y = np.random.normal(size=2500) * 2 + 5

    data = pd.DataFrame(data=dict(x=x, y=y)).sort_values(by="x")
    source = ColumnDataSource(data)

    p = figure(x_axis_type="datetime", tools='pan,wheel_zoom,box_zoom,reset,save')

    p.line(data['x'], data['y'], line_color="gray", line_width=1)

    low_box = BoxAnnotation(top=2, fill_alpha=0.1, fill_color='red')
    mid_box = BoxAnnotation(bottom=2, top=6, fill_alpha=0.1, fill_color='green')
    high_box = BoxAnnotation(bottom=6, fill_alpha=0.1, fill_color='red')

    p.add_layout(low_box)
    p.add_layout(mid_box)
    p.add_layout(high_box)

    p.title.text = "Glucose Range"
    p.xgrid[0].grid_line_color = None
    p.ygrid[0].grid_line_alpha = 0.5
    p.xaxis.axis_label = 'Time'
    p.yaxis.axis_label = 'Value'

    doc.add_root(column(p, p))


apps = {'/': Application(FunctionHandler(make_document))}

print('visit http://localhost:5006')
server = Server(apps, port=5006)
server.start()

IOLoop.current().start()
