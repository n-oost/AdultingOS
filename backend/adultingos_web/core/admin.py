"""
Admin registrations for the AdultingOS core app.

Why this module exists
----------------------
The Django admin provides a convenient interface for administrators and developers
to inspect and manage identity snapshots, supporting documents, and submitted
applications. This module registers the important models and configures list
views and search to make common administrative tasks easier.

Purpose
-------
Expose models with safe defaults (e.g., redact or make sensitive fields read-only
in the admin), provide filters for common fields, and enable quick navigation for
support workflows and debugging.

"""

from django.contrib import admin
from .models import (
    Task, Tag, UserProfile,
    LegalName, PersonalInformation, Address, ContactInformation,
    SupportingDocument, FoundationalDocumentsSnapshot,
    SINApplication, PassportReference, PassportGuarantor,
    PassportApplication, OntarioProvincialIdApplication, OSAPApplication
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'age', 'occupation', 'is_student', 'profile_completeness']
    list_filter = ['is_student', 'has_dependents', 'has_health_insurance']
    search_fields = ['user__username', 'occupation']

@admin.register(LegalName)
class LegalNameAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'middle_name', 'last_name']
    search_fields = ['first_name', 'last_name']

@admin.register(PersonalInformation)
class PersonalInformationAdmin(admin.ModelAdmin):
    list_display = ['legal_name', 'date_of_birth', 'sex']
    list_filter = ['sex']
    search_fields = ['legal_name__first_name', 'legal_name__last_name']

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['street_address', 'city', 'province', 'postal_code']
    list_filter = ['province']
    search_fields = ['street_address', 'city', 'postal_code']

@admin.register(ContactInformation)
class ContactInformationAdmin(admin.ModelAdmin):
    list_display = ['email_address', 'primary_phone_number']
    search_fields = ['email_address', 'primary_phone_number']

@admin.register(SupportingDocument)
class SupportingDocumentAdmin(admin.ModelAdmin):
    list_display = ['document_type', 'issuing_authority', 'document_number', 'issue_date', 'expiry_date']
    list_filter = ['document_type', 'functional_role']
    search_fields = ['document_number', 'issuing_authority']
    date_hierarchy = 'issue_date'

@admin.register(FoundationalDocumentsSnapshot)
class FoundationalDocumentsSnapshotAdmin(admin.ModelAdmin):
    list_display = ['user', 'last_verified']
    search_fields = ['user__username']
    date_hierarchy = 'created_at'

@admin.register(SINApplication)
class SINApplicationAdmin(admin.ModelAdmin):
    list_display = ['user', 'application_type', 'submission_method', 'status', 'created_at']
    list_filter = ['status', 'submission_method', 'application_type']
    search_fields = ['user__username']
    date_hierarchy = 'created_at'
    readonly_fields = ['version']

@admin.register(PassportReference)
class PassportReferenceAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'relationship', 'is_family']
    list_filter = ['is_family']
    search_fields = ['full_name']

@admin.register(PassportGuarantor)
class PassportGuarantorAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'years_known']
    search_fields = ['full_name']

@admin.register(PassportApplication)
class PassportApplicationAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['user__username']
    date_hierarchy = 'created_at'
    readonly_fields = ['version']

    def get_readonly_fields(self, request, obj=None):
        # Make canadian_passport_number read-only if it exists
        if obj and obj.guarantor:
            return self.readonly_fields + ('guarantor__canadian_passport_number',)
        return self.readonly_fields

@admin.register(OntarioProvincialIdApplication)
class OntarioProvincialIdApplicationAdmin(admin.ModelAdmin):
    list_display = ['user', 'application_type', 'status', 'is_surrendering_existing_id']
    list_filter = ['status', 'application_type', 'is_surrendering_existing_id']
    search_fields = ['user__username']
    date_hierarchy = 'created_at'
    readonly_fields = ['version']

@admin.register(OSAPApplication)
class OSAPApplicationAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'get_dependency_status', 'created_at']
    list_filter = ['status']
    search_fields = ['user__username']
    date_hierarchy = 'created_at'
    readonly_fields = ['version']

    def get_dependency_status(self, obj):
        return obj.dependency_information.get('status', 'Unknown')
    get_dependency_status.short_description = 'Dependency Status'

# Register Task and Tag models
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'priority', 'category', 'completed', 'due_date']
    list_filter = ['completed', 'priority', 'category']
    search_fields = ['title', 'description', 'user__username']
    date_hierarchy = 'due_date'

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
