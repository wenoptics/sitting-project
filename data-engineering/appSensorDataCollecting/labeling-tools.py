"""

"""

import requests
import pandas as pd
from bokeh import events
from bokeh.application import Application
from bokeh.application.handlers import FunctionHandler
from bokeh.models import ColumnDataSource, HoverTool, SaveTool, WheelZoomTool, PanTool, ResetTool, Div, BoxAnnotation, \
    CustomJS, Span
from bokeh.models.widgets import TextInput, Button
from bokeh.plotting import figure, curdoc
from bokeh.layouts import row, widgetbox, column
import numpy as np
from bokeh.server.server import Server
from tornado.ioloop import IOLoop


def display_event(div, attributes=[], style = 'float:left;clear:left;font_size=10pt'):
    "Build a suitable CustomJS to display the current event in the div model."
    return CustomJS(args=dict(div=div), code="""
        var attrs = %s; var args = [];
        for (var i = 0; i<attrs.length; i++) {
            args.push(attrs[i] + '=' + Number(cb_obj[attrs[i]]).toFixed(2));
        }
        var line = "<span style=%r><b>" + cb_obj.event_name + "</b>(" + args.join(", ") + ")</span>\\n";
        var text = div.text.concat(line);
        var lines = text.split("\\n")
        if (lines.length > 35)
            lines.shift();
        div.text = lines.join("\\n");
    """ % (attributes, style))


def make_document(doc):
    print(doc)

    # Create some random data
    x = np.random.random(2500) * 140 - 20
    y = np.random.normal(size=2500) * 2 + 5

    data = pd.DataFrame(data=dict(x=x, y=y)).sort_values(by="x")
    source = ColumnDataSource(data)

    p = figure(x_axis_type="datetime", tools='pan,wheel_zoom,box_zoom,reset,save')

    p.line(data['x'], data['y'], line_color="gray", line_width=1)

    mid_box = BoxAnnotation(left=2, right=6, fill_alpha=0.1, fill_color='green')

    vline = Span(location=0, dimension='height', line_color='red', line_width=3)

    p.renderers.extend([vline])

    # p.add_layout(low_box)
    p.add_layout(mid_box)
    # p.add_layout(high_box)

    p.title.text = "Glucose Range"
    p.xgrid[0].grid_line_color = None
    p.ygrid[0].grid_line_alpha = 0.5
    p.xaxis.axis_label = 'Time'
    p.yaxis.axis_label = 'Value'

    div = Div(width=400, height=p.plot_height, height_policy="fixed")

    ## Events with no attributes
    p.js_on_event(events.LODStart, display_event(div))  # Start of LOD display
    p.js_on_event(events.LODEnd, display_event(div))  # End of LOD display

    ## Events with attributes
    point_attributes = ['x', 'y', 'sx', 'sy']  # Point events
    # wheel_attributes = point_attributes + ['delta']  # Mouse wheel event
    # pan_attributes = point_attributes + ['delta_x', 'delta_y']  # Pan event
    # pinch_attributes = point_attributes + ['scale']  # Pinch event

    point_events = [
        events.Tap,
        # events.DoubleTap, events.Press,
        # events.MouseMove, events.MouseEnter, events.MouseLeave,
        # events.PinchStart, events.PinchEnd,
        # events.PanStart, events.PanEnd,
    ]

    for event in point_events:
        p.js_on_event(event, display_event(div, attributes=point_attributes))

    p.js_on_event(events.Tap, CustomJS(args=dict(vline=vline), code="""
        vline.location = cb_obj['x'];
    """))

    btn_start = Button(label="Mark as START", button_type="success")
    btn_end = Button(label="Mark as END", button_type="success")
    btn_start.js_on_event(events.ButtonClick,
        CustomJS(args=dict(div=div, mid_box=mid_box, vline=vline), code="""
                    mid_box.left = vline.location;
                    mid_box.right = null;
                """)
    )
    btn_end.js_on_event(events.ButtonClick,
        CustomJS(args=dict(div=div, mid_box=mid_box, vline=vline), code="""
                    mid_box.right = vline.location;
                """)
    )
    # btn_end.on_click()

    # p.js_on_event(events.MouseWheel, display_event(div, attributes=wheel_attributes))
    # p.js_on_event(events.Pan, display_event(div, attributes=pan_attributes))
    # p.js_on_event(events.Pinch, display_event(div, attributes=pinch_attributes))

    doc.add_root(column(row(p, div), btn_start, btn_end))


apps = {'/': Application(FunctionHandler(make_document))}

print('visit http://localhost:5002')
server = Server(apps, port=5002)
server.start()

IOLoop.current().start()
