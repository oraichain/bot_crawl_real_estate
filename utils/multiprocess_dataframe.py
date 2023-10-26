from abc import ABC, abstractmethod
from multiprocessing import Pool
from multiprocessing import cpu_count

import pandas as pd
import numpy as np

from utils.measure_time import measure_time

class DataFrameProcessor(ABC):
    
    def __init__(self, df=None, df_path=None):
        if df is not None:
            self.df = df
        elif df_path is not None:
            self.df = pd.read_csv(df_path)

    @abstractmethod
    def process_df(self, df):
        pass

    @measure_time
    def parallel_process(self, void=False):
        pool = Pool(processes=cpu_count())

        df_splits = np.array_split(self.df, cpu_count())
        if void:
            pool.map(self.process_df, df_splits)
            pool.close()
            pool.join()
        else:
            results = pool.map(self.process_df, df_splits)
            pool.close()
            pool.join()
            self.out_df = pd.concat(results, ignore_index=True)

    def save_output_df(self, out_path):
        self.out_df.to_csv(out_path, index=False)
