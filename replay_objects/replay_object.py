import pandas as pd


class ReplayObject:
    data: dict = None
    dataframe: pd.DataFrame = None

    def __init__(self):
        self.data = {}

    def update_data(self, frame_idx, data):
        self.data[frame_idx] = data

    def set_dataframe(self, dataframe):
        self.dataframe = dataframe

    def get_data(self):
        return self.data

    def get_dataframe(self):
        return self.dataframe
