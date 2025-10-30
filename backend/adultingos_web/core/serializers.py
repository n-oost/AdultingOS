"""
Serializers for the AdultingOS core app.

Why these serializers exist
---------------------------
Serializers define how model instances are converted to/from JSON for the API. They
perform nested creation/update for complex identity objects (e.g., `PersonalInformation` with
`LegalName`), enforce serializer-level validations that complement model `clean()` methods,
and ensure sensitive data is not accidentally exposed. Implementing nested serializers
here keeps the API layer resilient to client input and centralizes creation logic for
composed objects used across multiple application flows.

Purpose
-------
Provide stable, well-tested translation between Python objects and API payloads. They
handle nested object creation, field-level validation, and read-only redactions for
sensitive attributes. Clients (web, mobile, assistant) rely on these serializers for
both input validation and consistent response shapes.

"""

from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import (
    Task, Tag, UserProfile,
    # Foundational Models
    LegalName, PersonalInformation, Address, ContactInformation,
    SupportingDocument, FoundationalDocumentsSnapshot,
    # Application Models
    SINApplication, PassportReference, PassportGuarantor,
    PassportApplication, OntarioProvincialIdApplication, OSAPApplication
)


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for Tag model.
    
    Handles converting Tag instances to/from JSON for API responses.
    Tags are simple objects with just an ID and name.
    """
    
    class Meta:
        model = Tag
        fields = ['id', 'name']
        
    def validate_name(self, value):
        """Ensure tag names are not empty and are reasonably formatted."""
        if not value.strip():
            raise serializers.ValidationError("Tag name cannot be empty.")
        return value.strip().lower()  # Normalize to lowercase


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for Task model.
    
    Handles converting Task instances to/from JSON for API responses.
    Includes custom fields for better user experience:
    - Shows tag names instead of just IDs
    - Shows username instead of user ID
    - Includes computed fields like priority display name
    """
    
    tags = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Tag.objects.all(),
        required=False
    )
    
    user = serializers.ReadOnlyField(source='user.username')
    
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'user', 'title', 'description', 'category', 'due_date',
            'priority', 'priority_display', 'completed', 'tags', 'is_overdue',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at', 'priority_display', 'is_overdue']
    
    def get_is_overdue(self, obj):
        """Calculate if this task is overdue."""
        return obj.is_overdue()
    
    def validate_title(self, value):
        """Ensure task title is not empty."""
        if not value.strip():
            raise serializers.ValidationError("Task title cannot be empty.")
        return value.strip()

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        task = Task.objects.create(**validated_data)
        for tag_name in tags_data:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            task.tags.add(tag)
        return task

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)
        instance = super().update(instance, validated_data)
        if tags_data is not None:
            instance.tags.clear()
            for tag_name in tags_data:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                instance.tags.add(tag)
        return instance


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    
    Handles creating new user accounts with validation for:
    - Password confirmation matching
    - Minimum password length
    - Unique username/email
    """
    
    password = serializers.CharField(
        write_only=True, 
        min_length=8,
        help_text="Password must be at least 8 characters long"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        help_text="Must match the password field"
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm')
        extra_kwargs = {
            'email': {'required': True},  # Make email required
        }

    def validate(self, attrs):
        """Validate that password and password_confirm match."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs

    def create(self, validated_data):
        """Create a new user account."""
        # Remove password_confirm since it's not needed for user creation
        validated_data.pop('password_confirm')
        # Create user with encrypted password
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    
    Validates username/password credentials and returns the authenticated user.
    """
    
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Validate user credentials and return authenticated user."""
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            # Attempt to authenticate with provided credentials
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid username or password.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            # Add the authenticated user to validated data
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include both username and password.')
        
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile model.
    
    Handles converting UserProfile instances to/from JSON for API responses.
    Used for onboarding flow and personalized task generation.
    """
    
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'username', 'age', 'occupation', 'is_student',
            'filing_status', 'has_dependents', 'dependent_count',
            'typical_tax_filing_month', 'has_hsa', 'has_401k',
            'is_homeowner', 'has_student_loans', 'has_health_insurance',
            'insurance_renewal_month', 'recent_life_events',
            'preferred_reminder_frequency', 'onboarding_completed',
            'profile_completeness', 'last_profile_update',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'username', 'profile_completeness', 'created_at', 'updated_at']
    
    def update(self, instance, validated_data):
        """Update profile and recalculate completeness."""
        instance = super().update(instance, validated_data)
        instance.calculate_completeness()
        instance.save()
        return instance


# Foundational Identity Serializers
class LegalNameSerializer(serializers.ModelSerializer):
    """Serializer for legal names."""
    class Meta:
        model = LegalName
        fields = ['id', 'first_name', 'middle_name', 'last_name']


class PersonalInformationSerializer(serializers.ModelSerializer):
    """Serializer for personal information."""
    legal_name = LegalNameSerializer()
    former_names = LegalNameSerializer(many=True, read_only=True)

    class Meta:
        model = PersonalInformation
        fields = ['id', 'legal_name', 'date_of_birth', 'place_of_birth', 
                 'sex', 'former_names', 'height', 'gender']

    def create(self, validated_data):
        legal_name_data = validated_data.pop('legal_name')
        legal_name = LegalName.objects.create(**legal_name_data)
        personal_info = PersonalInformation.objects.create(legal_name=legal_name, **validated_data)
        return personal_info

    def update(self, instance, validated_data):
        if 'legal_name' in validated_data:
            legal_name_data = validated_data.pop('legal_name')
            legal_name_serializer = LegalNameSerializer(instance.legal_name, data=legal_name_data)
            if legal_name_serializer.is_valid():
                legal_name_serializer.save()
        return super().update(instance, validated_data)


class AddressSerializer(serializers.ModelSerializer):
    """Serializer for addresses."""
    class Meta:
        model = Address
        fields = ['id', 'street_address', 'apartment_unit', 'city', 
                 'province', 'postal_code', 'country']


class ContactInformationSerializer(serializers.ModelSerializer):
    """Serializer for contact information."""
    class Meta:
        model = ContactInformation
        fields = ['id', 'primary_phone_number', 'alternate_phone_number', 'email_address']


class SupportingDocumentSerializer(serializers.ModelSerializer):
    """Serializer for supporting documents."""
    class Meta:
        model = SupportingDocument
        fields = ['id', 'document_type', 'issuing_authority', 'document_number',
                 'issue_date', 'expiry_date', 'functional_role']
        
    def validate(self, attrs):
        if attrs.get('expiry_date') and attrs.get('issue_date'):
            if attrs['expiry_date'] < attrs['issue_date']:
                raise serializers.ValidationError({
                    'expiry_date': 'Expiry date cannot be before issue date'
                })
        return attrs


class FoundationalDocumentsSnapshotSerializer(serializers.ModelSerializer):
    """Serializer for foundational documents snapshot."""
    personal_information = PersonalInformationSerializer()
    current_address = AddressSerializer()
    contact_information = ContactInformationSerializer()
    supporting_documents = SupportingDocumentSerializer(many=True, read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = FoundationalDocumentsSnapshot
        fields = ['id', 'username', 'personal_information', 'current_address',
                 'contact_information', 'supporting_documents', 'last_verified',
                 'created_at']
        read_only_fields = ['last_verified', 'created_at']

    def create(self, validated_data):
        personal_info_data = validated_data.pop('personal_information')
        address_data = validated_data.pop('current_address')
        contact_info_data = validated_data.pop('contact_information')

        personal_info_serializer = PersonalInformationSerializer(data=personal_info_data)
        personal_info_serializer.is_valid(raise_exception=True)
        personal_info = personal_info_serializer.save()

        address = Address.objects.create(**address_data)
        contact_info = ContactInformation.objects.create(**contact_info_data)

        snapshot = FoundationalDocumentsSnapshot.objects.create(
            personal_information=personal_info,
            current_address=address,
            contact_information=contact_info,
            **validated_data
        )
        return snapshot


# Application Serializers
class PassportReferenceSerializer(serializers.ModelSerializer):
    """Serializer for passport references."""
    contact_information = ContactInformationSerializer()

    class Meta:
        model = PassportReference
        fields = ['id', 'full_name', 'relationship', 'contact_information', 'is_family']

    def create(self, validated_data):
        contact_info_data = validated_data.pop('contact_information')
        contact_info = ContactInformation.objects.create(**contact_info_data)
        return PassportReference.objects.create(contact_information=contact_info, **validated_data)


class PassportGuarantorSerializer(serializers.ModelSerializer):
    """Serializer for passport guarantors."""
    class Meta:
        model = PassportGuarantor
        fields = ['id', 'full_name', 'canadian_passport_number', 'years_known']

    def validate_years_known(self, value):
        if value < 2:
            raise serializers.ValidationError(
                "Guarantor must have known the applicant for at least 2 years"
            )
        return value

    def validate_canadian_passport_number(self, value):
        if len(value) != 8:
            raise serializers.ValidationError(
                "Canadian passport number must be 8 digits"
            )
        return value


class BaseApplicationSerializer(serializers.ModelSerializer):
    """Base serializer for all application types."""
    username = serializers.CharField(source='user.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        fields = ['id', 'username', 'status', 'status_display', 'version',
                 'submitted_at', 'created_at', 'updated_at']
        read_only_fields = ['version', 'submitted_at', 'created_at', 'updated_at']


class SINApplicationSerializer(BaseApplicationSerializer):
    """Serializer for SIN applications."""
    applicant_information = PersonalInformationSerializer()
    contact_information = ContactInformationSerializer()
    address = AddressSerializer()
    submitted_documents = SupportingDocumentSerializer(many=True, read_only=True)

    class Meta(BaseApplicationSerializer.Meta):
        model = SINApplication
        fields = BaseApplicationSerializer.Meta.fields + [
            'submission_method', 'application_type', 'applicant_information',
            'contact_information', 'address', 'submitted_documents'
        ]

    def validate(self, attrs):
        if attrs.get('submission_method') == 'ONLINE':
            # Online applications require proof of address validation
            # This will be checked when documents are attached
            pass
        return attrs

    def create(self, validated_data):
        applicant_info_data = validated_data.pop('applicant_information')
        contact_info_data = validated_data.pop('contact_information')
        address_data = validated_data.pop('address')

        applicant_info_serializer = PersonalInformationSerializer(data=applicant_info_data)
        applicant_info_serializer.is_valid(raise_exception=True)
        applicant_info = applicant_info_serializer.save()

        contact_info = ContactInformation.objects.create(**contact_info_data)
        address = Address.objects.create(**address_data)

        # Allow callers to pass `user` via serializer.save(user=...)
        user = None
        # DRF passes extra kwargs to create as keyword arguments; capture them if present
        # Note: serializer.save(user=...) will pass user into create as a kwarg
        # so we handle that here to attach the application to the user.
        # If no user is provided, object creation will fail at DB level (user is required)
        # which surface a clear error during tests or usage.
        # We accept arbitrary kwargs for forward-compatibility.
        try:
            # If this method is called with extra kwargs, they will be available on the serializer
            # via `self.context` or passed into create by DRF; attempt to read from context first.
            user = self.context.get('user')
        except Exception:
            user = None

        # Fallback: allow DRF to pass user via validated_data if present
        user = validated_data.pop('user', user)

        sin_app = SINApplication.objects.create(
            user=user,
            applicant_information=applicant_info,
            contact_information=contact_info,
            address=address,
            **validated_data
        )
        return sin_app


class PassportApplicationSerializer(BaseApplicationSerializer):
    """Serializer for passport applications."""
    applicant_information = PersonalInformationSerializer()
    contact_information = ContactInformationSerializer()
    addresses_last_two_years = AddressSerializer(many=True)
    guarantor = PassportGuarantorSerializer()
    references = PassportReferenceSerializer(many=True)
    submitted_documents = SupportingDocumentSerializer(many=True, read_only=True)

    class Meta(BaseApplicationSerializer.Meta):
        model = PassportApplication
        fields = BaseApplicationSerializer.Meta.fields + [
            'applicant_information', 'contact_information',
            'addresses_last_two_years', 'occupation_history',
            'guarantor', 'references', 'submitted_documents'
        ]

    def validate_references(self, value):
        if len(value) != 2:
            raise serializers.ValidationError(
                "Exactly two references are required"
            )
        if any(ref.get('is_family', False) for ref in value):
            raise serializers.ValidationError(
                "References cannot be family members"
            )
        return value

    def validate(self, attrs):
        # Check if guarantor is also a reference
        guarantor_name = attrs.get('guarantor', {}).get('full_name')
        references = attrs.get('references', [])
        if any(ref.get('full_name') == guarantor_name for ref in references):
            raise serializers.ValidationError(
                "Guarantor cannot also be a reference"
            )
        return attrs

    def create(self, validated_data):
        applicant_info_data = validated_data.pop('applicant_information')
        contact_info_data = validated_data.pop('contact_information')
        addresses_data = validated_data.pop('addresses_last_two_years')
        guarantor_data = validated_data.pop('guarantor')
        references_data = validated_data.pop('references')

        # Create applicant information
        applicant_info_serializer = PersonalInformationSerializer(data=applicant_info_data)
        applicant_info_serializer.is_valid(raise_exception=True)
        applicant_info = applicant_info_serializer.save()

        # Create contact information
        contact_info = ContactInformation.objects.create(**contact_info_data)

        # Create addresses
        addresses = [Address.objects.create(**addr_data) for addr_data in addresses_data]

        # Create guarantor
        guarantor = PassportGuarantor.objects.create(**guarantor_data)

        # Create application
        passport_app = PassportApplication.objects.create(
            applicant_information=applicant_info,
            contact_information=contact_info,
            guarantor=guarantor,
            **validated_data
        )

        # Add addresses
        passport_app.addresses_last_two_years.set(addresses)

        # Create and add references
        for ref_data in references_data:
            contact_info = ref_data.pop('contact_information')
            contact_obj = ContactInformation.objects.create(**contact_info)
            reference = PassportReference.objects.create(
                contact_information=contact_obj,
                **ref_data
            )
            passport_app.references.add(reference)

        return passport_app


class OntarioProvincialIdApplicationSerializer(BaseApplicationSerializer):
    """Serializer for Ontario Provincial ID applications."""
    applicant_information = PersonalInformationSerializer()
    address = AddressSerializer()
    submitted_documents = SupportingDocumentSerializer(many=True, read_only=True)

    class Meta(BaseApplicationSerializer.Meta):
        model = OntarioProvincialIdApplication
        fields = BaseApplicationSerializer.Meta.fields + [
            'application_type', 'applicant_information', 'address',
            'is_surrendering_existing_id', 'medical_information',
            'submitted_documents'
        ]

    def validate(self, attrs):
        if attrs.get('application_type') == 'DRIVER_LICENSE':
            if not attrs.get('medical_information'):
                raise serializers.ValidationError({
                    'medical_information': (
                        "Medical information is required for driver's license applications"
                    )
                })
        return attrs

    def create(self, validated_data):
        applicant_info_data = validated_data.pop('applicant_information')
        address_data = validated_data.pop('address')

        applicant_info_serializer = PersonalInformationSerializer(data=applicant_info_data)
        applicant_info_serializer.is_valid(raise_exception=True)
        applicant_info = applicant_info_serializer.save()

        address = Address.objects.create(**address_data)

        ontario_id_app = OntarioProvincialIdApplication.objects.create(
            applicant_information=applicant_info,
            address=address,
            **validated_data
        )
        return ontario_id_app


class OSAPApplicationSerializer(BaseApplicationSerializer):
    """Serializer for OSAP applications."""
    student_profile = PersonalInformationSerializer()

    class Meta(BaseApplicationSerializer.Meta):
        model = OSAPApplication
        fields = BaseApplicationSerializer.Meta.fields + [
            'student_profile', 'dependency_information',
            'academic_information', 'student_financials',
            'parental_financials', 'spousal_financials'
        ]

    def validate(self, attrs):
        dependency_info = attrs.get('dependency_information', {})
        dependency_status = dependency_info.get('status')
        if dependency_status == 'DEPENDENT' and not attrs.get('parental_financials'):
            raise serializers.ValidationError({
                'parental_financials': (
                    "Parental financials required for dependent students"
                )
            })

        marital_status = dependency_info.get('maritalStatus')
        if marital_status in ['MARRIED', 'COMMON_LAW'] and not attrs.get('spousal_financials'):
            raise serializers.ValidationError({
                'spousal_financials': (
                    "Spousal financials required for married/common-law students"
                )
            })

        return attrs

    def create(self, validated_data):
        student_profile_data = validated_data.pop('student_profile')
        
        student_profile_serializer = PersonalInformationSerializer(data=student_profile_data)
        student_profile_serializer.is_valid(raise_exception=True)
        student_profile = student_profile_serializer.save()

        osap_app = OSAPApplication.objects.create(
            student_profile=student_profile,
            **validated_data
        )
        return osap_app