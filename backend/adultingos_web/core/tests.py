from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError
from .models import SupportingDocument
from .serializers import (
    PersonalInformationSerializer,
    SINApplicationSerializer,
    SupportingDocumentSerializer
)


class SerializerTests(TestCase):
    def setUp(self):
        """Create test user and common test data."""
        self.user = User.objects.create_user(username='tester', password='pass12345')
        self.personal_info_data = {
            'legal_name': {
                'first_name': 'Jane',
                'middle_name': 'Q',
                'last_name': 'Doe'
            },
            'date_of_birth': '1990-01-01',
            'place_of_birth': 'Toronto',
            'sex': 'F',
            'height': '170.00',
            'gender': 'Female'
        }

    def test_personal_information_serializer_create(self):
        """Test creating personal information via serializer."""
        serializer = PersonalInformationSerializer(data=self.personal_info_data)
        self.assertTrue(serializer.is_valid(), msg=serializer.errors)
        personal_info = serializer.save()

        self.assertIsNotNone(personal_info.id)
        self.assertEqual(personal_info.legal_name.first_name, 'Jane')
        self.assertEqual(personal_info.sex, 'F')

    def test_personal_information_serializer_update(self):
        """Test updating existing personal information."""
        # First create the initial record
        serializer = PersonalInformationSerializer(data=self.personal_info_data)
        self.assertTrue(serializer.is_valid())
        personal_info = serializer.save()

        # Update with new data
        update_data = {
            'legal_name': {
                'first_name': 'Janet',  # Changed from Jane
                'middle_name': 'Q',
                'last_name': 'Doe'
            },
            'date_of_birth': '1990-01-01',  # Same
            'place_of_birth': 'Vancouver',  # Changed from Toronto
            'sex': 'F',
            'height': '171.50',  # Changed from 170.00
            'gender': 'Female'
        }

        update_serializer = PersonalInformationSerializer(
            personal_info,
            data=update_data,
            partial=True
        )
        self.assertTrue(update_serializer.is_valid(), msg=update_serializer.errors)
        updated_info = update_serializer.save()

        # Verify changes
        self.assertEqual(updated_info.legal_name.first_name, 'Janet')
        self.assertEqual(updated_info.place_of_birth, 'Vancouver')
        self.assertEqual(float(updated_info.height), 171.50)

    def test_sin_application_serializer_create(self):
        """Test creating a SIN application with all required fields."""
        contact_data = {
            'primary_phone_number': '555-1111',
            'alternate_phone_number': '',
            'email_address': 'jane@example.com'
        }

        address_data = {
            'street_address': '1 Test St',
            'apartment_unit': '',
            'city': 'Toronto',
            'province': 'ON',
            'postal_code': 'M1M1M1',
            'country': 'Canada'
        }

        sin_payload = {
            'submission_method': 'ONLINE',
            'application_type': 'NEW',
            'applicant_information': self.personal_info_data,
            'contact_information': contact_data,
            'address': address_data,
            'status': 'DRAFT'
        }

        serializer = SINApplicationSerializer(data=sin_payload)
        self.assertTrue(serializer.is_valid(), msg=serializer.errors)
        sin_app = serializer.save(user=self.user)

        self.assertIsNotNone(sin_app.id)
        self.assertEqual(sin_app.user, self.user)
        self.assertEqual(sin_app.applicant_information.legal_name.first_name, 'Jane')
        self.assertEqual(sin_app.status, 'DRAFT')

    def test_online_sin_application_requires_proof_of_address(self):
        """Test that online SIN applications require proof of address."""
        contact_data = {
            'primary_phone_number': '555-1111',
            'email_address': 'jane@example.com'
        }

        address_data = {
            'street_address': '1 Test St',
            'city': 'Toronto',
            'province': 'ON',
            'postal_code': 'M1M1M1',
            'country': 'Canada'
        }

        # Create a SIN application without proof of address
        sin_payload = {
            'submission_method': 'ONLINE',  # Online requires proof of address
            'application_type': 'NEW',
            'applicant_information': self.personal_info_data,
            'contact_information': contact_data,
            'address': address_data,
            'status': 'SUBMITTED'  # Try to submit without proof
        }

        serializer = SINApplicationSerializer(data=sin_payload)
        self.assertTrue(serializer.is_valid(), msg=serializer.errors)
        
        # Should raise validation error on save since online submission
        # requires proof of address and we're trying to submit
        with self.assertRaises(ValidationError) as context:
            sin_app = serializer.save(user=self.user)
        
        self.assertIn('proof of address', str(context.exception))

    def test_sin_application_status_transitions(self):
        """Test valid and invalid status transitions for SIN applications."""
        # Create initial application in DRAFT
        contact_data = {'primary_phone_number': '555-1111', 'email_address': 'jane@example.com'}
        address_data = {
            'street_address': '1 Test St', 'city': 'Toronto',
            'province': 'ON', 'postal_code': 'M1M1M1'
        }

        initial_payload = {
            'submission_method': 'MAIL',  # Mail doesn't require proof of address
            'application_type': 'NEW',
            'applicant_information': self.personal_info_data,
            'contact_information': contact_data,
            'address': address_data,
            'status': 'DRAFT'
        }

        serializer = SINApplicationSerializer(data=initial_payload)
        self.assertTrue(serializer.is_valid())
        sin_app = serializer.save(user=self.user)
        
        # Valid transition: DRAFT -> SUBMITTED
        update_data = {'status': 'SUBMITTED'}
        update_serializer = SINApplicationSerializer(sin_app, data=update_data, partial=True)
        self.assertTrue(update_serializer.is_valid())
        sin_app = update_serializer.save()
        self.assertEqual(sin_app.status, 'SUBMITTED')

        # Invalid transition: SUBMITTED -> DRAFT (can't go backwards)
        update_data = {'status': 'DRAFT'}
        update_serializer = SINApplicationSerializer(sin_app, data=update_data, partial=True)
        self.assertTrue(update_serializer.is_valid())
        with self.assertRaises(ValidationError) as context:
            sin_app = update_serializer.save()
        self.assertIn('status transition', str(context.exception))
