from django.urls import path
from tokens.views import MintTokensView, SyncBalanceView

urlpatterns = [
    path('tokens/mint/', MintTokensView.as_view(), name='mint_tokens'),
    path('tokens/sync/', SyncBalanceView.as_view(), name='sync_balance'),
]