import logging

from celery import shared_task

from .models import WechatAccount
from .services import sync_wechat_account


logger = logging.getLogger(__name__)


@shared_task
def sync_wechat_account_task(account_id):
    account = WechatAccount.objects.get(pk=account_id)
    result = sync_wechat_account(account)
    logger.info("Wechat account sync completed: %s", result)
    return result


@shared_task
def sync_all_wechat_accounts():
    results = []
    queryset = WechatAccount.objects.filter(is_active=True).exclude(source_type=WechatAccount.SourceType.MANUAL)
    for account in queryset.iterator():
        try:
            result = sync_wechat_account(account)
            results.append(result)
            logger.info("Wechat account sync completed: %s", result)
        except Exception as exc:
            result = {"account_id": account.pk, "account_name": account.name, "error": str(exc)}
            results.append(result)
            logger.warning("Wechat account sync failed: %s", result)
    return results
