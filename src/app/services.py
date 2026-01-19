import pandas as pd

from src.app.repository import DataRepository
from src.app.config import settings


class RecommendationService:
    def __init__(self, repo: DataRepository):
        self.repo = repo
        self.W_CLICK = settings.w_click
        self.W_CART = settings.w_cart
        self.W_PURCHASE = settings.w_purchase
        self.ITEMS_LIMIT = settings.items_limit
        self.BRAND_LIMIT = settings.brand_limit

    def calculate_global_top(self) -> list:
        """
        Рассчитать глобальный (общий) топ рекомендаций.
        """
        df = self.repo.get_all_data()

        df['u_click'] = df.index.where(df['click'] > 0)
        df['u_cart'] = df.index.where(df['add_to_cart'] > 0)
        df['u_purchase'] = df.index.where(df['purchase'] > 0)

        try:
            stats = df.groupby(['pid', 'brand']).agg(
                u_clicks=('u_click', 'nunique'),
                u_carts=('u_cart', 'nunique'),
                u_purchases=('u_purchase', 'nunique')
            ).reset_index()

            stats['score'] = (
                stats['u_clicks'] * self.W_CLICK + 
                stats['u_carts'] * self.W_CART + 
                stats['u_purchases'] * self.W_PURCHASE
            )

            top_products = stats.sort_values('score', ascending=False)
            return self._apply_brand_limit(top_products).head(self.ITEMS_LIMIT)['pid'].tolist()
        finally:
            df.drop(columns=['u_click', 'u_cart', 'u_purchase'], inplace=True)

    def _apply_brand_limit(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Применить ограничение на N товаров одного бренда.
        """
        brand_occurrence = df.groupby('brand').cumcount()
        return df[brand_occurrence < self.BRAND_LIMIT]

    def get_recommendations(self, user_id: int) -> list:
        """
        Получить топ рекомендаций.
        """
        user_history = self.repo.get_user_history(user_id)

        if user_history is None:
            return self.repo.get_global_top()
        
        return self._calculate_personalized_recs(user_history)
    
    def _calculate_personalized_recs(self, user_df: pd.DataFrame) -> list:
        """
        Рассчитать персонализированный топ рекомендаций.
        """
        purchased_pids = user_df[user_df['purchase'] > 0]['pid'].unique()
        interest_df = user_df[~user_df['pid'].isin(purchased_pids)]
        global_top = self.repo.get_global_top()

        if interest_df.empty:
            return [p for p in global_top if p not in purchased_pids]

        stats = interest_df.groupby(['pid', 'brand']).agg({
            'click': 'sum',
            'add_to_cart': 'sum'
        }).reset_index()

        stats['score'] = stats['click'] * self.W_CLICK + stats['add_to_cart'] * self.W_CART
        
        sorted_stats = stats.sort_values('score', ascending=False)
        recommendations = self._apply_brand_limit(sorted_stats).head(self.ITEMS_LIMIT)['pid'].tolist()

        if len(recommendations) < self.ITEMS_LIMIT:
            for pid in global_top:
                if pid not in recommendations and pid not in purchased_pids:
                    recommendations.append(pid)
                if len(recommendations) == self.ITEMS_LIMIT:
                    break
                    
        return recommendations[:self.ITEMS_LIMIT]
