import plotly.graph_objects as go
import datetime as dt
import pandas as pd


class Graph():
    __instance = None
    figure = None

    buyColor = 'rgba(210, 0, 0, 1)'
    sellColor = 'rgba(0, 0, 210, 1)'

    @staticmethod
    def getInstance():
        if Graph.__instance == None:
            Graph()
        return Graph.__instance

    def __init__(self):
        if Graph.__instance != None:
            raise Exception("This class is a singleton!")
        Graph.__instance = self
        self.figure = go.Figure()

    @staticmethod
    def render():
        self = Graph.getInstance()
        self.figure.show()
        self.figure = go.Figure()  # Reset graph when rendering.

    @staticmethod
    def setTitle(title):
        self = Graph.getInstance()
        self.figure.update_layout(
            title=go.layout.Title(text=title),
            title_font_size=20
        )

    @staticmethod
    def addCandleSticks(x, open, high, low, close, name):
        self = Graph.getInstance()
        self.figure.add_trace(
            go.Candlestick(
                x=x,
                open=open,
                high=high,
                low=low,
                close=close,
                name=name
            )
        )

    @staticmethod
    def addIndicator(x, y, name, color):
        self = Graph.getInstance()
        self.figure.add_trace(
            go.Scatter(
                x=x,
                y=y,
                name=name,
                line_color=color
            )
        )

    @staticmethod
    def addAction(x, y, name, action, isBuy):
        self = Graph.getInstance()
        color = self.buyColor if isBuy else self.sellColor
        self.figure.add_annotation(x=x,
                                   y=y,
                                   text="{} #{}".format(action, name),
                                   showarrow=True,
                                   align="center",
                                   arrowhead=2,
                                   arrowsize=1,
                                   arrowwidth=2,
                                   arrowcolor=color,
                                   bordercolor="#c7c7c7",
                                   borderwidth=2,
                                   borderpad=2,
                                   bgcolor=color,
                                   font=dict(
                                       size=16,
                                       color="#ffffff"
                                   ),
                                   opacity=1)
