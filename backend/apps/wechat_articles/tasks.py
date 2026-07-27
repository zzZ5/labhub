from celery import shared_task

from .models import WechatAccount
from .services import sync_wechat_account


@shared_task
def sync_wechat_account_task(account_id):
    account = WechatAccount.objects.get(pk=account_id)
    return sync_wechat_account(account)


@shared_task
def sync_all_wechat_accounts():
    results = []
    queryset = WechatAccount.objects.filter(is_active=True).exclude(source_type=WechatAccount.SourceType.MANUAL)
    for account in queryset.iterator():
        try:
            results.append(sync_wechat_account(account))
        except Exception as exc:
            results.append({"account_id": account.pk, "account_name": account.name, "error": str(exc)})
    return results

