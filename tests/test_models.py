"""Tests for Expiring Token models.

Classes:
    ExpiringTokenTestCase: Tests ExpiringToken.
"""
from django.utils import timezone
from datetime import timedelta
from time import sleep

from django.contrib.auth.models import User
from django.test import TestCase

from drf_expiring_tokens.models import ExpiringToken


class ExpiringTokenTestCase(TestCase):

    """Test case for Expiring Token model."""

    def setUp(self):
        """Create a user and associated token."""
        self.username = 'test'
        self.email = 'test@test.com'
        self.password = 'test'
        self.user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password
        )

        self.key = 'abc123'
        self.token = ExpiringToken.objects.create(
            user=self.user,
            key=self.key
        )

    def test_expired_indated(self):
        """Check the expired method returns false for an indated token."""
        self.assertFalse(self.token.expired())

    def test_expired_outdated(self):
        """Check the expired method return true for an outdated token."""
        # Crude, but necessary as auto_now_add field can't be changed.
        with self.settings(EXPIRING_TOKEN_LIFESPAN=timedelta(milliseconds=1)):
            sleep(0.001)
            self.assertTrue(self.token.expired())

    def test_refresh(self):
        """Check that a refresh updates the created time"""
        pre_refresh_time = timezone.now()
        self.token.refresh()
        self.assertTrue(self.token.created > pre_refresh_time)

    def test_refresh_after_expiration(self):
        """Check that a refresh doesn't change the time on an expired token"""
        old_created_time = self.token.created
        with self.settings(EXPIRING_TOKEN_LIFESPAN=timedelta(milliseconds=1)):
            sleep(0.001)
            self.assertTrue(self.token.expired())
            self.token.refresh()
            self.assertEqual(self.token.created, old_created_time)
