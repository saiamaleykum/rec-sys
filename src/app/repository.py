import pandas as pd
from typing import Optional, List


class DataRepository:
    _instance: Optional["DataRepository"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.df = None
            cls._instance.global_top = []
        return cls._instance

    def load_from_csv(self, path: str)-> None:
        self.df = pd.read_csv(path)
        self.df.set_index('uid', inplace=True)
        self.df.sort_index(inplace=True)

    def set_global_top(self, pids: List[int]) -> None:
        self.global_top = pids

    def get_all_data(self) -> pd.DataFrame:
        return self.df

    def get_global_top(self) -> List[int]:
        return self.global_top
    
    def get_user_history(self, uid: int) -> Optional[pd.DataFrame]:
        if uid not in self.df.index:
            return None
        
        return self.df.loc[[uid]]
    