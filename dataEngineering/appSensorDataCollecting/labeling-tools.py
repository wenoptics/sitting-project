"""

"""
import queue
from queue import Queue
from threading import Thread

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

# from dataServer import start_data_server, data_q
from dataEngineering.appSensorDataCollecting.DataServer import start_data_server, data_q

current_selected_sitting_posture = {'val': 0}

csv_file = open(f'data/collect-{0}.csv', 'a')

def write_csv_row(data):
    for i in range(len(data['time'])):
        for k in data.keys():
            csv_file.write(f"{data[k][i]},")
        csv_file.write("\n")

def update_from_sensor(datasource: ColumnDataSource):
    acceleration = []
    accelerationIncludingGravity = []
    rotation = []
    rotationRate = []
    orientation = []
    timestamp = []

    while True:
        try:
            d = data_q.get_nowait()
        except queue.Empty:
            break
        else:
            acceleration.append(d['acceleration'])
            accelerationIncludingGravity.append(d['accelerationIncludingGravity'])
            rotation.append(d['rotation'])
            rotationRate.append(d['rotationRate'])
            orientation.append(d['orientation'])
            timestamp.append(d['timestamp'])

    acceleration = pd.DataFrame.from_dict(acceleration)
    accelerationIncludingGravity = pd.DataFrame.from_dict(accelerationIncludingGravity)
    rotation = pd.DataFrame.from_dict(rotation)
    rotationRate = pd.DataFrame.from_dict(rotationRate)
    orientation = pd.DataFrame.from_dict(orientation)

    if len(acceleration) == 0:
        return

    datasource.stream(dict(
        time=timestamp,
        acc_x=acceleration.x,
        acc_y=acceleration.y,
        acc_z=acceleration.z,
        accg_x=accelerationIncludingGravity.x,
        accg_y=accelerationIncludingGravity.y,
        accg_z=accelerationIncludingGravity.z,
        rot_a=rotation.alpha,
        rot_b=rotation.beta,
        rot_g=rotation.gamma,
        rotr_a=rotationRate.alpha,
        rotr_b=rotationRate.beta,
        rotr_g=rotationRate.gamma,
    ), 2000)

    write_csv_row(
        dict(
            time=timestamp,
            acc_x=acceleration.x,
            acc_y=acceleration.y,
            acc_z=acceleration.z,
            accg_x=accelerationIncludingGravity.x,
            accg_y=accelerationIncludingGravity.y,
            accg_z=accelerationIncludingGravity.z,
            rot_a=rotation.alpha,
            rot_b=rotation.beta,
            rot_g=rotation.gamma,
            rotr_a=rotationRate.alpha,
            rotr_b=rotationRate.beta,
            rotr_g=rotationRate.gamma,
        )
    )


def make_document(doc):
    print(doc)

    data = ColumnDataSource(dict(
        time=[],

        acc_x=[],
        acc_y=[],
        acc_z=[],
        accg_x=[],
        accg_y=[],
        accg_z=[],
        rot_a=[],
        rot_b=[],
        rot_g=[],
        rotr_a=[],
        rotr_b=[],
        rotr_g=[],

        # angle_dev=[]
    ))

    p = figure(x_axis_type="datetime", tools='pan,wheel_zoom,box_zoom,reset,save', plot_width=1100)

    p.line(x='time', y='acc_x', line_color="red", line_width=1, source=data)
    p.line(x='time', y='acc_y', line_color="green", line_width=1, source=data)
    p.line(x='time', y='acc_z', line_color="blue", line_width=1, source=data)
    p.line(x='time', y='rot_a', line_color="cyan", line_width=1, source=data)
    p.line(x='time', y='rot_b', line_color="black", line_width=1, source=data)
    p.line(x='time', y='rot_g', line_color="orange", line_width=1, source=data)

    mid_box = BoxAnnotation(left=2, right=6, fill_alpha=0.1, fill_color='blue')

    vline = Span(location=0, dimension='height', line_color='red', line_width=3)

    p.renderers.extend([vline])

    # p.add_layout(low_box)
    p.add_layout(mid_box)
    # p.add_layout(high_box)

    p.title.text = "Sitting Project Labeling Tool v0.1"
    p.xgrid[0].grid_line_color = None
    p.ygrid[0].grid_line_alpha = 0.5
    p.xaxis.axis_label = 'Time'
    p.yaxis.axis_label = 'Value'

    div = Div(width=400, height=p.plot_height, height_policy="fixed")

    ## Events with no attributes
    # p.js_on_event(events.LODStart, display_event(div))  # Start of LOD display
    # p.js_on_event(events.LODEnd, display_event(div))  # End of LOD display

    ## Events with attributes
    # point_attributes = ['x', 'y', 'sx', 'sy']  # Point events
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

    # for event in point_events:
    #     p.js_on_event(event, display_event(div, attributes=point_attributes))

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

    def write_csv():
        print(mid_box.left, mid_box.right)

    btn_sit1 = Button(label="cross-leg")
    btn_sit2 = Button(label="lean-right")
    btn_sit3 = Button(label="lean-back")
    # btn_sit4 = Button(label="sit4")

    btn_sit1.js_on_event(events.ButtonClick,
                        CustomJS(
                            args=dict(div=div, mid_box=mid_box, vline=vline),
                            code="""
                       mid_box.right = vline.location;
                       console.log(mid_box.left, mid_box.right, "cross-leg");
                   """)
                        )
    btn_sit2.js_on_event(events.ButtonClick,
                        CustomJS(
                            args=dict(div=div, mid_box=mid_box, vline=vline),
                            code="""
                       mid_box.right = vline.location;
                       console.log(mid_box.left, mid_box.right, "lean-right");
                   """)
                        )
    btn_sit3.js_on_event(events.ButtonClick,
                        CustomJS(
                            args=dict(div=div, mid_box=mid_box, vline=vline),
                            code="""
                       mid_box.right = vline.location;
                       console.log(mid_box.left, mid_box.right, "lean-back");
                   """)
                        )
    # btn_sit4.js_on_event(events.ButtonClick,
    #                     CustomJS(
    #                         args=dict(div=div, mid_box=mid_box, vline=vline),
    #                         code="""
    #                    mid_box.right = vline.location;
    #                    console.log(mid_box.left, mid_box.right, "sit4");
    #                """)
    #                     )

    btn_write= Button(label="Write CSV")
    btn_write.on_click(lambda : write_csv())

    # p.js_on_event(events.MouseWheel, display_event(div, attributes=wheel_attributes))
    # p.js_on_event(events.Pan, display_event(div, attributes=pan_attributes))
    # p.js_on_event(events.Pinch, display_event(div, attributes=pinch_attributes))

    doc.add_periodic_callback(lambda: update_from_sensor(data), 60)
    doc.add_root(
        column(
            row(p, div),
            row(btn_start),
            row(column(
                btn_sit1,
                btn_sit2,
                btn_sit3,
                ) )
        ))


if __name__ == '__main__':
    Thread(target=start_data_server).start()

    apps = {'/': Application(FunctionHandler(make_document))}

    print('visit http://localhost:5002')
    server = Server(apps, port=5002)
    server.start()

    IOLoop.current().start()
