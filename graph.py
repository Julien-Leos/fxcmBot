import plotly.graph_objects as go
import datetime as dt
import pandas as pd


class Graph():
    __instance = None
    figure = None

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
        self.figure = go.Figure() # Reset graph when rendering.

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
    def setTitle(title):
        self = Graph.getInstance()
        self.figure.update_layout(
            title=go.layout.Title(text=title),
            title_font_size=20
        )