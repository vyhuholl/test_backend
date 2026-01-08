"""Management command to clean up expired blacklisted tokens."""

import logging
from datetime import datetime

from django.core.management.base import BaseCommand

from authentication.models import TokenBlacklist


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Django management command to clean up expired tokens from blacklist."""
    
    help = "Remove expired tokens from the blacklist table"
    
    def handle(self, *args: tuple, **options: dict) -> None:
        """
        Execute the cleanup command.
        
        Deletes all TokenBlacklist entries where expires_at < now.
        """
        now = datetime.now()
        
        # Delete expired tokens
        deleted_count, _ = TokenBlacklist.objects.filter(expires_at__lt=now).delete()
        
        # Log results
        message = f"Cleaned up {deleted_count} expired blacklisted token(s)"
        self.stdout.write(self.style.SUCCESS(message))
        logger.info(message)
