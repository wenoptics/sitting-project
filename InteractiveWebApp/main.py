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
from InteractiveWebApp.DataServer import start_data_server, data_q

current_accg = np.array([0, 0, 0])
reset_accg = np.array([
    -0.28,
    -9.65,
    2.58
])


def calc_angle_dev(current_accg):
    global reset_accg
    current_accg = current_accg.reshape(1, 3)
    a, b = current_accg, reset_accg

    # print(current_ac0.6140963949678593
    # -0.3425715324411591
    # -9.819727847992226cg.shape)
    if len(current_accg.shape) == 1 or current_accg.shape[1] == 0:
        return np.nan

    return np.arccos(
        a.dot(b.T) / (np.linalg.norm(a, axis=1) * np.linalg.norm(b))
    ) * 180 / np.pi


def update_accg(data):
    global current_accg, reset_accg
    current_accg = np.array([
        data['accg_x'].tolist()[-1],
        data['accg_y'].tolist()[-1],
        data['accg_z'].tolist()[-1]
    ])

    return (
        data['accg_x'].tolist()[-1],
        data['accg_y'].tolist()[-1],
        data['accg_z'].tolist()[-1],
        calc_angle_dev(current_accg)
    )


def update_from_sensor():
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
        return None,None,None,None

    # datasource.stream(dict(
    #     time=timestamp,
    #     acc_x=acceleration.x,
    #     acc_y=acceleration.y,
    #     acc_z=acceleration.z,
    #     accg_x=accelerationIncludingGravity.x,
    #     accg_y=accelerationIncludingGravity.y,
    #     accg_z=accelerationIncludingGravity.z,
    #     rot_a=rotation.alpha,
    #     rot_b=rotation.beta,
    #     rot_g=rotation.gamma,
    #     rotr_a=rotationRate.alpha,
    #     rotr_b=rotationRate.beta,
    #     rotr_g=rotationRate.gamma,
    # ), 2000)

    return update_accg(
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

    div = Div(text="""
        <p>Waiting for connection ... <p>
    """, width=200, height=100)

    def periodic_cb():

        x,y,z,d = update_from_sensor()

        if x is None:
            return

        x = round(x, 2)
        y = round(y, 2)
        z = round(z, 2)
        d[0] = round(d[0], 2)

        val_d = d[0]
        if d[0] > 5:
            val_d = f'<span style="color: orange">{d[0]}<span>'
        if d[0] > 15:
            val_d = f'<span style="color: Red">{d[0]}<span>'

        value = f'x:<span id="x_val">{x}</span><br>' \
                   f'y:<span id="y_val">{y}</span><br>' \
                   f'z:<span id="z_val">{z}</span><br><br>' \
                   f'Deviation angle is: {val_d}'

        div.text = ("\n"
         "            <div>\n"
         "                <style>\n"
         "                    p {text-align: center;}\n"
         "                </style>\n"
         "                <p>\n"
         f"                    {value}\n"
         "                </p>\n"
         "            </div>")

    doc.add_periodic_callback(periodic_cb, 60)
    doc.add_root(
        column(
            div
        )
    )


if __name__ == '__main__':
    Thread(target=start_data_server).start()

    apps = {'/': Application(FunctionHandler(make_document))}

    print('visit http://localhost:8081')
    server = Server(apps, port=8081)
    server.start()

    IOLoop.current().start()
