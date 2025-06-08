from django.urls import path
from tokens.views import MintTokensView, SyncBalanceView, WithdrawTokensView
from tokens import views as token_views

urlpatterns = [
    path('tokens/mint/', MintTokensView.as_view(), name='mint_tokens'),
    path('tokens/sync/', SyncBalanceView.as_view(), name='sync_balance'),
    path('wallet/balance/', token_views.TokenBalanceView.as_view(), name='token_balance'),
    path('wallet/add/', token_views.add_tokens, name='add_tokens'),
    path('wallet/remove/', token_views.remove_tokens, name='remove_tokens'),
    path('wallet/withdraw/', WithdrawTokensView.as_view(), name='withdraw_tokens'),
]