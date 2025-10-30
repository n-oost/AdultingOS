"""
Core data models for the AdultingOS `core` app.

Why these models exist
----------------------
This module implements a hybrid identity and application model designed to support
two common needs simultaneously:

- A canonical, per-user `FoundationalDocumentsSnapshot` used for fast profile
    pre-fill and reuse across multiple government application flows.
- Versioned, auditable application models (SIN, Passport, Ontario ID, OSAP) that
    preserve submission history, status transitions, and validations specific to
    each program.

Design rationale and important notes
-----------------------------------
- Models aim to be normalized and reusable (e.g., `LegalName`, `Address`,
    `ContactInformation`) so the same objects can be referenced in snapshots and
    application records without duplicating core identity data.
- Domain rules are enforced via `clean()` methods and serializers to keep
    business logic close to the data (examples: guarantor rules, proof-of-address
    requirements for online SIN applications, medical info for driver's licenses).
- Sensitive fields (for example, SIN or guarantor passport numbers) should be
    encrypted at rest and masked when exposed by APIs; consider adding an
    encrypted-field library and API redaction in serializers/admin.

Purpose
-------
Provide a single, well-documented place for identity and application models
that the API, admin UI, and assistant features can depend on. These types
are intentionally explicit about relationships and validation so client apps
can rely on server-side enforcement.

"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# Foundational Identity Models
class LegalName(models.Model):
    """Model for storing legal name information."""
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Legal Name"
        verbose_name_plural = "Legal Names"

class PersonalInformation(models.Model):
    """Model for storing core personal information."""
    SEX_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('X', 'X')
    ]
    
    legal_name = models.OneToOneField(LegalName, on_delete=models.PROTECT)
    date_of_birth = models.DateField()
    place_of_birth = models.CharField(max_length=200)
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)
    former_names = models.ManyToManyField(LegalName, related_name='former_names', blank=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, help_text="Height in centimeters")
    gender = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.legal_name} - DOB: {self.date_of_birth}"

    class Meta:
        verbose_name = "Personal Information"
        verbose_name_plural = "Personal Information Records"

class Address(models.Model):
    """Model for storing address information."""
    street_address = models.CharField(max_length=200)
    apartment_unit = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=7)
    country = models.CharField(max_length=100, default='Canada')

    def __str__(self):
        addr = f"{self.street_address}"
        if self.apartment_unit:
            addr += f" Unit {self.apartment_unit}"
        addr += f", {self.city}, {self.province} {self.postal_code}"
        return addr

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"

class ContactInformation(models.Model):
    """Model for storing contact information."""
    primary_phone_number = models.CharField(max_length=20)
    alternate_phone_number = models.CharField(max_length=20, blank=True)
    email_address = models.EmailField()

    def __str__(self):
        return f"{self.email_address} - {self.primary_phone_number}"

    class Meta:
        verbose_name = "Contact Information"
        verbose_name_plural = "Contact Information Records"

class SupportingDocument(models.Model):
    """Model for storing supporting document information."""
    DOCUMENT_TYPES = [
        ('PASSPORT', 'Passport'),
        ('DRIVERS_LICENSE', 'Driver\'s License'),
        ('BIRTH_CERT', 'Birth Certificate'),
        ('CITIZENSHIP', 'Citizenship Card/Certificate'),
        ('PR_CARD', 'Permanent Resident Card'),
        ('HEALTH_CARD', 'Health Card'),
        ('SIN_CARD', 'Social Insurance Number Card'),
        ('BANK_STATEMENT', 'Bank Statement'),
        ('UTILITY_BILL', 'Utility Bill')
    ]
    
    FUNCTIONAL_ROLES = [
        ('IDENTITY', 'Proof of Identity'),
        ('ADDRESS', 'Proof of Address'),
        ('STATUS', 'Proof of Status'),
        ('INCOME', 'Proof of Income'),
        ('EDUCATION', 'Proof of Education')
    ]

    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    issuing_authority = models.CharField(max_length=200)
    document_number = models.CharField(max_length=50)
    issue_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    functional_role = models.CharField(max_length=50, choices=FUNCTIONAL_ROLES)

    def __str__(self):
        return f"{self.get_document_type_display()} - {self.document_number}"

    def clean(self):
        if self.expiry_date and self.expiry_date < self.issue_date:
            raise ValidationError("Expiry date cannot be before issue date")

    class Meta:
        verbose_name = "Supporting Document"
        verbose_name_plural = "Supporting Documents"

class FoundationalDocumentsSnapshot(models.Model):
    """Container model for storing the user's canonical identity information."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='foundational_documents')
    personal_information = models.OneToOneField(PersonalInformation, on_delete=models.PROTECT)
    current_address = models.ForeignKey(Address, on_delete=models.PROTECT, related_name='current_resident')
    contact_information = models.OneToOneField(ContactInformation, on_delete=models.PROTECT)
    supporting_documents = models.ManyToManyField(SupportingDocument, blank=True)
    last_verified = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Identity Snapshot - {self.user.username}"

    class Meta:
        verbose_name = "Foundational Documents Snapshot"
        verbose_name_plural = "Foundational Documents Snapshots"

# Application Models
class BaseApplication(models.Model):
    """Abstract base class for all application types."""
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('REVIEW', 'Under Review'),
        ('SUBMITTED', 'Submitted'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    version = models.PositiveIntegerField(default=1)
    submitted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class SINApplication(BaseApplication):
    """Model for Social Insurance Number applications."""
    SUBMISSION_METHODS = [
        ('ONLINE', 'Online'),
        ('MAIL', 'By Mail'),
        ('IN_PERSON', 'In Person')
    ]
    
    APPLICATION_TYPES = [
        ('NEW', 'New SIN'),
        ('REPLACEMENT', 'Replacement'),
        ('UPDATE', 'Information Update'),
        ('CONFIRMATION', 'Confirmation of SIN')
    ]

    submission_method = models.CharField(max_length=20, choices=SUBMISSION_METHODS)
    application_type = models.CharField(max_length=20, choices=APPLICATION_TYPES)
    applicant_information = models.ForeignKey(PersonalInformation, on_delete=models.PROTECT)
    contact_information = models.ForeignKey(ContactInformation, on_delete=models.PROTECT)
    address = models.ForeignKey(Address, on_delete=models.PROTECT)
    submitted_documents = models.ManyToManyField(SupportingDocument)

    def clean(self):
        if self.submission_method == 'ONLINE':
            proof_of_address = self.submitted_documents.filter(functional_role='ADDRESS').exists()
            if not proof_of_address:
                raise ValidationError("Online applications require proof of address")

    class Meta:
        verbose_name = "SIN Application"
        verbose_name_plural = "SIN Applications"

class PassportReference(models.Model):
    """Model for passport references."""
    full_name = models.CharField(max_length=200)
    relationship = models.CharField(max_length=100)
    contact_information = models.ForeignKey(ContactInformation, on_delete=models.PROTECT)
    is_family = models.BooleanField()

    def __str__(self):
        return f"{self.full_name} - {self.relationship}"

class PassportGuarantor(models.Model):
    """Model for passport guarantors."""
    full_name = models.CharField(max_length=200)
    canadian_passport_number = models.CharField(max_length=8)
    years_known = models.PositiveIntegerField()

    def clean(self):
        if self.years_known < 2:
            raise ValidationError("Guarantor must have known the applicant for at least 2 years")
        if not len(self.canadian_passport_number) == 8:
            raise ValidationError("Canadian passport number must be 8 digits")

    def __str__(self):
        return f"{self.full_name} - Known for {self.years_known} years"

class PassportApplication(BaseApplication):
    """Model for passport applications."""
    applicant_information = models.ForeignKey(PersonalInformation, on_delete=models.PROTECT)
    contact_information = models.ForeignKey(ContactInformation, on_delete=models.PROTECT)
    addresses_last_two_years = models.ManyToManyField(Address)
    occupation_history = models.JSONField(default=list)
    guarantor = models.ForeignKey(PassportGuarantor, on_delete=models.PROTECT)
    references = models.ManyToManyField(PassportReference)
    submitted_documents = models.ManyToManyField(SupportingDocument)

    def clean(self):
        # Check if guarantor is also a reference
        if self.references.filter(full_name=self.guarantor.full_name).exists():
            raise ValidationError("Guarantor cannot also be a reference")
        # Check number of references
        if self.references.count() != 2:
            raise ValidationError("Exactly two references are required")
        # Check if any reference is family
        if self.references.filter(is_family=True).exists():
            raise ValidationError("References cannot be family members")

    class Meta:
        verbose_name = "Passport Application"
        verbose_name_plural = "Passport Applications"

class OntarioProvincialIdApplication(BaseApplication):
    """Model for Ontario Provincial ID applications."""
    APPLICATION_TYPES = [
        ('DRIVER_LICENSE', 'Driver\'s License'),
        ('PHOTO_CARD', 'Photo Card')
    ]

    application_type = models.CharField(max_length=20, choices=APPLICATION_TYPES)
    applicant_information = models.ForeignKey(PersonalInformation, on_delete=models.PROTECT)
    address = models.ForeignKey(Address, on_delete=models.PROTECT)
    is_surrendering_existing_id = models.BooleanField(default=False)
    medical_information = models.JSONField(null=True, blank=True)
    submitted_documents = models.ManyToManyField(SupportingDocument)

    def clean(self):
        if self.application_type == 'DRIVER_LICENSE' and not self.medical_information:
            raise ValidationError("Medical information is required for driver's license applications")

    class Meta:
        verbose_name = "Ontario Provincial ID Application"
        verbose_name_plural = "Ontario Provincial ID Applications"

class OSAPApplication(BaseApplication):
    """Model for Ontario Student Assistance Program applications."""
    student_profile = models.ForeignKey(PersonalInformation, on_delete=models.PROTECT)
    dependency_information = models.JSONField()
    academic_information = models.JSONField()  # Includes study period
    student_financials = models.JSONField()
    parental_financials = models.JSONField(null=True, blank=True)
    spousal_financials = models.JSONField(null=True, blank=True)

    def clean(self):
        dependency_status = self.dependency_information.get('status')
        if dependency_status == 'DEPENDENT' and not self.parental_financials:
            raise ValidationError("Parental financials required for dependent students")
        
        marital_status = self.dependency_information.get('maritalStatus')
        if marital_status in ['MARRIED', 'COMMON_LAW'] and not self.spousal_financials:
            raise ValidationError("Spousal financials required for married/common-law students")

    class Meta:
        verbose_name = "OSAP Application"
        verbose_name_plural = "OSAP Applications"

class Tag(models.Model):
    """
    Model representing a tag for categorizing and organizing tasks.
    
    Tags allow users to group related tasks together (e.g., "work", "personal", "urgent").
    Each tag has a unique name and can be applied to multiple tasks.
    """
    # Tag name - must be unique across all tags
    name = models.CharField(max_length=50, unique=True, help_text="Unique name for this tag")

    def __str__(self):
        """Return the tag name when the object is displayed."""
        return self.name

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ['name']  # Sort tags alphabetically


class Task(models.Model):
    """
    Model representing a task/to-do item in the AdultingOS system.
    
    Tasks are the core data model for the application. Each task belongs to a user
    and can have priorities, due dates, categories, and tags for organization.
    """
    
    class Priority(models.IntegerChoices):
        """Priority levels for tasks, from lowest to highest importance."""
        LOW = 1, "Low"
        MEDIUM = 2, "Medium" 
        HIGH = 3, "High"
        URGENT = 4, "Urgent"
        CRITICAL = 5, "Critical"
    
    # Core task fields
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='tasks',
        help_text="The user who owns this task"
    )
    title = models.CharField(
        max_length=200, 
        help_text="Short description of what needs to be done"
    )
    description = models.TextField(
        blank=True, 
        help_text="Optional detailed description of the task"
    )
    
    # Organization fields
    category = models.CharField(
        max_length=100, 
        default="general",
        help_text="Category to group related tasks (e.g., 'finance', 'health')"
    )
    tags = models.ManyToManyField(
        Tag, 
        blank=True, 
        related_name='tasks',
        help_text="Tags for flexible task organization"
    )
    
    # Status and priority
    priority = models.IntegerField(
        choices=Priority.choices, 
        default=Priority.MEDIUM,
        help_text="Task priority level"
    )
    completed = models.BooleanField(
        default=False, 
        help_text="Whether this task has been completed"
    )
    
    # Timing fields
    due_date = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="When this task is due (optional)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this task was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this task was last modified"
    )
    
    def mark_completed(self):
        """Mark this task as completed and save to database."""
        self.completed = True
        self.save()
    
    def mark_incomplete(self):
        """Mark this task as incomplete and save to database."""
        self.completed = False
        self.save()
    
    def is_overdue(self):
        """Check if this task is past its due date."""
        if not self.due_date:
            return False
        return timezone.now() > self.due_date and not self.completed
    
    def __str__(self):
        """Return the task title when the object is displayed."""
        return f"{self.title} ({self.get_priority_display()})"

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        # Order by priority (highest first), then due date (earliest first)
        ordering = ['-priority', 'due_date']

class UserProfile(models.Model):
    """Stores user's life context for personalized task generation."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Demographics
    age = models.IntegerField(null=True, blank=True)
    occupation = models.CharField(max_length=100, null=True, blank=True)
    is_student = models.BooleanField(default=False)
    
    # Financial context
    filing_status = models.CharField(
        max_length=20, 
        choices=[
            ('single', 'Single'),
            ('married_joint', 'Married Filing Jointly'),
            ('married_separate', 'Married Filing Separately'),
            ('head_of_household', 'Head of Household'),
        ],
        null=True, 
        blank=True
    )
    has_dependents = models.BooleanField(default=False)
    dependent_count = models.IntegerField(default=0)
    
    # Tax context
    typical_tax_filing_month = models.IntegerField(
        null=True, 
        blank=True,
        help_text="1-12, when user typically files taxes"
    )
    has_hsa = models.BooleanField(default=False)
    has_401k = models.BooleanField(default=False)
    is_homeowner = models.BooleanField(default=False)
    has_student_loans = models.BooleanField(default=False)
    
    # Health & benefits
    has_health_insurance = models.BooleanField(default=False)
    insurance_renewal_month = models.IntegerField(null=True, blank=True)
    
    # Life events (tracked for milestone tasks)
    recent_life_events = models.JSONField(default=list, blank=True)
    
    # Preferences
    preferred_reminder_frequency = models.CharField(
        max_length=20,
        choices=[
            ('weekly', 'Weekly'),
            ('biweekly', 'Bi-weekly'),
            ('monthly', 'Monthly'),
        ],
        default='weekly'
    )
    
    # Profile completion tracking
    onboarding_completed = models.BooleanField(default=False)
    profile_completeness = models.IntegerField(default=0)
    last_profile_update = models.DateTimeField(auto_now=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profile for {self.user.username}"
    
    def calculate_completeness(self):
        """Calculate profile completeness percentage."""
        fields = [
            self.age, self.occupation, self.filing_status,
            self.typical_tax_filing_month, 
        ]
        filled = sum(1 for f in fields if f is not None)
        total = len(fields) + 6  # Boolean fields
        
        self.profile_completeness = int((filled / total) * 100)
        return self.profile_completeness