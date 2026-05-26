from datetime import datetime

from django.contrib.auth import get_user_model
from django.db import models
from django.test import TestCase

from backend.utils.model_utils import SoftDeleteModelMixin

User = get_user_model()


class SoftDeleteModel(SoftDeleteModelMixin, models.Model):
    """Test model for SoftDeleteManager and SoftDeleteModelMixin"""

    name = models.CharField(max_length=100)

    class Meta:
        app_label = "tests"


class SoftDeleteManagerTestCase(TestCase):
    """Test cases for SoftDeleteManager"""

    def setUp(self):
        """Set up test data"""
        # Create test instances
        self.active_obj = SoftDeleteModel.objects.create(name="Active Object")
        self.deleted_obj = SoftDeleteModel.objects.create(name="Deleted Object")
        self.deleted_obj.is_removed = True
        self.deleted_obj.save()

    def test_get_queryset_filters_deleted_objects(self):
        """Test that get_queryset only returns non-deleted objects"""
        # Using the default manager (which should be SoftDeleteManager)
        queryset = SoftDeleteModel.available_objects.all()

        # Should only contain the active object
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), self.active_obj)
        self.assertNotIn(self.deleted_obj, queryset)

    def test_manager_returns_correct_type(self):
        """Test that the manager returns the correct queryset type"""
        queryset = SoftDeleteModel.available_objects.all()
        self.assertIsInstance(queryset, models.QuerySet)

    def test_manager_filters_by_is_removed_field(self):
        """Test that the manager specifically filters by is_removed=False"""
        # Create another deleted object
        another_deleted = SoftDeleteModel.objects.create(name="Another Deleted")
        another_deleted.is_removed = True
        another_deleted.save()

        # Get all objects using default manager
        all_objects = SoftDeleteModel.objects.all()
        self.assertEqual(all_objects.count(), 3)  # active + 2 deleted

        # Get available objects
        available_objects = SoftDeleteModel.available_objects.all()
        self.assertEqual(available_objects.count(), 1)  # only active

        # Verify the active object is in available
        self.assertIn(self.active_obj, available_objects)

        # Verify deleted objects are not in available
        self.assertNotIn(self.deleted_obj, available_objects)
        self.assertNotIn(another_deleted, available_objects)


class SoftDeleteModelMixinTestCase(TestCase):
    """Test cases for SoftDeleteModelMixin"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.obj = SoftDeleteModel.objects.create(name="Test Object")

    def test_soft_delete_sets_fields_correctly(self):
        """Test that soft delete sets is_removed, deleted_at, and deleted_by"""
        # Perform soft delete
        self.obj.delete(soft=True, deleted_by=self.user)

        # Refresh from database
        self.obj.refresh_from_db()

        # Check fields
        self.assertTrue(self.obj.is_removed)
        self.assertIsNotNone(self.obj.deleted_at)
        self.assertEqual(self.obj.deleted_by, self.user)

    def test_soft_delete_without_user(self):
        """Test soft delete without specifying deleted_by"""
        # Perform soft delete without user
        self.obj.delete(soft=True)

        # Refresh from database
        self.obj.refresh_from_db()

        # Check fields
        self.assertTrue(self.obj.is_removed)
        self.assertIsNotNone(self.obj.deleted_at)
        self.assertIsNone(self.obj.deleted_by)

    def test_hard_delete_calls_super(self):
        """Test that hard delete calls super().delete()"""
        obj_id = self.obj.id

        # Perform hard delete
        self.obj.delete(soft=False)

        # Object should be deleted from database
        with self.assertRaises(SoftDeleteModel.DoesNotExist):
            SoftDeleteModel.objects.get(id=obj_id)

    def test_delete_method_preserves_other_fields(self):
        """Test that delete method doesn't affect other fields"""
        original_name = self.obj.name

        # Perform soft delete
        self.obj.delete(soft=True, deleted_by=self.user)

        # Refresh from database
        self.obj.refresh_from_db()

        # Name should remain unchanged
        self.assertEqual(self.obj.name, original_name)

    def test_deleted_at_is_datetime(self):
        """Test that deleted_at is a datetime object"""
        # Perform soft delete
        self.obj.delete(soft=True)

        # Refresh from database
        self.obj.refresh_from_db()

        # Check that deleted_at is a datetime
        self.assertIsInstance(self.obj.deleted_at, datetime)

    def test_soft_delete_updates_only_specified_fields(self):
        """Test that only specified fields are updated in save()"""
        # This is more of an integration test, but ensures the update_fields works
        self.obj.delete(soft=True, deleted_by=self.user)

        # The object should still exist and be findable with regular manager
        obj_from_db = SoftDeleteModel.objects.get(id=self.obj.id)
        self.assertTrue(obj_from_db.is_removed)
        self.assertEqual(obj_from_db.deleted_by, self.user)


class SoftDeleteIntegrationTestCase(TestCase):
    """Integration tests for soft delete functionality"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username="testuser", password="testpass")

        # Create multiple objects
        self.obj1 = SoftDeleteModel.objects.create(name="Object 1")
        self.obj2 = SoftDeleteModel.objects.create(name="Object 2")
        self.obj3 = SoftDeleteModel.objects.create(name="Object 3")

    def test_available_objects_after_soft_deletes(self):
        """Test available_objects manager after performing soft deletes"""
        # Soft delete obj1 and obj3
        self.obj1.delete(soft=True, deleted_by=self.user)
        self.obj3.delete(soft=True)

        # Check available objects
        available = SoftDeleteModel.available_objects.all()
        self.assertEqual(available.count(), 1)
        self.assertEqual(available.first(), self.obj2)

        # All objects still exist in database
        all_objects = SoftDeleteModel.objects.all()
        self.assertEqual(all_objects.count(), 3)

    def test_mixed_soft_and_hard_deletes(self):
        """Test mixing soft and hard deletes"""
        # Soft delete obj1
        self.obj1.delete(soft=True)

        # Hard delete obj2
        self.obj2.delete(soft=False)

        # obj3 remains active
        self.obj3.is_removed = False  # ensure it's active

        # Available objects should only show obj3
        available = SoftDeleteModel.available_objects.all()
        self.assertEqual(available.count(), 1)
        self.assertEqual(available.first(), self.obj3)

        # All objects in database: obj1 (soft deleted), obj3 (active)
        # obj2 is hard deleted, so not in database
        all_objects = SoftDeleteModel.objects.all()
        self.assertEqual(all_objects.count(), 2)

        # Verify obj1 is soft deleted
        obj1_from_db = SoftDeleteModel.objects.get(id=self.obj1.id)
        self.assertTrue(obj1_from_db.is_removed)
