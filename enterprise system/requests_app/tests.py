from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase
from django.utils import timezone

from .models import Category, ServiceRequest, WorkOrder


class ServiceRequestModelTests(TestCase):
    """Original Lab 3 tests."""

    def setUp(self):
        user_model = get_user_model()
        self.requester = user_model.objects.create_user(username="requester")
        self.technician = user_model.objects.create_user(username="technician")
        self.category = Category.objects.create(name="Electrical")

    def make_request(self, **overrides):
        values = {
            "requester": self.requester,
            "category": self.category,
            "title": "Faulty socket",
            "description": "Socket does not supply power.",
            "location": "Software Engineering Lab",
            "priority": 2,
        }
        values.update(overrides)
        return ServiceRequest.objects.create(**values)

    def test_default_status_is_open(self):
        item = self.make_request()
        self.assertEqual(item.status, ServiceRequest.Status.OPEN)

    def test_priority_validator_rejects_zero(self):
        item = ServiceRequest(
            requester=self.requester,
            category=self.category,
            title="Invalid",
            description="Invalid priority.",
            location="Lab",
            priority=0,
        )
        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_database_constraint_rejects_priority_six(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.make_request(priority=6)

    def test_category_in_use_is_protected(self):
        self.make_request()
        with self.assertRaises(ProtectedError):
            self.category.delete()

    def test_request_accepts_only_one_work_order(self):
        item = self.make_request()
        WorkOrder.objects.create(
            service_request=item,
            technician=self.technician,
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                WorkOrder.objects.create(
                    service_request=item,
                    technician=self.technician,
                )


class DueDateTests(TestCase):
    """New tests for Task 1."""

    def setUp(self):
        self.requester = get_user_model().objects.create_user(username="requester")
        self.category = Category.objects.create(name="Electrical")

    def make_request(self, title, **extra):
        values = {
            "requester": self.requester,
            "category": self.category,
            "title": title,
            "description": "Synthetic laboratory data.",
            "location": "Lab 1",
            "priority": 2,
        }
        values.update(extra)
        return ServiceRequest.objects.create(**values)

    def test_due_at_is_optional(self):
        item = self.make_request("No due date")
        item.full_clean()
        self.assertIsNone(item.due_at)

    def test_query_returns_only_requests_due_before_cutoff(self):
        now = timezone.now()
        self.make_request("Due soon", due_at=now + timedelta(hours=2))
        self.make_request("Due later", due_at=now + timedelta(days=3))
        cutoff = now + timedelta(days=1)
        results = ServiceRequest.objects.filter(due_at__lt=cutoff)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().title, "Due soon")

    def test_status_and_due_at_index_exists(self):
        names = [index.name for index in ServiceRequest._meta.indexes]
        self.assertIn("req_status_due_idx", names)


class ResolutionRuleTests(TestCase):
    """New tests for Task 2."""

    def setUp(self):
        self.requester = get_user_model().objects.create_user(username="requester")
        self.category = Category.objects.create(name="Electrical")

    def build(self, **extra):
        values = {
            "requester": self.requester,
            "category": self.category,
            "title": "Synthetic rule test",
            "description": "Synthetic laboratory data.",
            "location": "Lab 1",
            "priority": 2,
        }
        values.update(extra)
        return ServiceRequest(**values)

    def test_resolved_without_resolved_at_fails(self):
        item = self.build(status="resolved", resolution_summary="Fixed.")
        with self.assertRaises(ValidationError) as ctx:
            item.full_clean()
        self.assertIn("resolved_at", ctx.exception.message_dict)

    def test_resolved_without_summary_fails(self):
        item = self.build(status="resolved", resolved_at=timezone.now())
        with self.assertRaises(ValidationError) as ctx:
            item.full_clean()
        self.assertIn("resolution_summary", ctx.exception.message_dict)

    def test_closed_with_blank_summary_fails(self):
        item = self.build(
            status="closed",
            resolved_at=timezone.now(),
            resolution_summary="   ",
        )
        with self.assertRaises(ValidationError) as ctx:
            item.full_clean()
        self.assertIn("resolution_summary", ctx.exception.message_dict)

    def test_resolved_with_both_values_passes(self):
        item = self.build(
            status="resolved",
            resolved_at=timezone.now(),
            resolution_summary="Replaced the faulty socket.",
        )
        item.full_clean()

    def test_open_request_does_not_need_summary(self):
        self.build(status="open").full_clean()
