# Foundational Identity Module - Implementation Decisions

**Date:** November 1, 2025  
**Status:** Implemented  
**Branch:** FOUNDATION

## Overview
This document captures key architectural and implementation decisions made for the Foundational Identity & Education Module (Ontario focus). These decisions affect the Django models, data flow, and API design for SIN, Passport, Ontario ID, and OSAP applications.

## Core Decisions

### 1. User Model
**Decision:** Use Django's built-in `django.contrib.auth.models.User`  
**Rationale:**
- Simplifies authentication integration with DRF Token Authentication
- Leverages existing Django ecosystem (admin, permissions, groups)
- UserProfile extension provides domain-specific fields without customizing auth
- Easier to extend later with custom user model if needed

**Trade-offs:**
- Cannot customize username field or add required fields to User directly
- Must maintain 1:1 UserProfile relationship for additional data

---

### 2. Encryption Library
**Decision:** Use `django-encrypted-model-fields` (v0.6.5+)  
**Rationale:**
- Compatible with Django 5.x (django-fernet-fields uses deprecated force_text)
- Uses Fernet symmetric encryption (cryptography library)
- Simple field-level encryption with minimal configuration
- Encrypted values stored as binary in database

**Configuration:**
```python
# settings.py
FIELD_ENCRYPTION_KEY = os.getenv('FIELD_ENCRYPTION_KEY', generated_from_SECRET_KEY)
```

**Encrypted Fields:**
- `SINApplication.sin_number` (9 digits)
- `PassportGuarantor.canadian_passport_number` (8 digits)
- Future: parental/spousal SIN in OSAP financials (via JSONField encryption)

**Admin Masking:**
- SIN: `***-***-123` (last 3 digits)
- Passport: `****1234` (last 4 digits)

---

### 3. Application Status Values
**Decision:** Use 6 standard statuses for all application types  
**Values:** `DRAFT`, `REVIEW`, `SUBMITTED`, `APPROVED`, `REJECTED`, `CANCELLED`

**Status Workflow:**
```
DRAFT → REVIEW → SUBMITTED → APPROVED/REJECTED/CANCELLED
  ↓         ↓         ↓
CANCELLED  CANCELLED  CANCELLED
```

**Rationale:**
- Covers common application lifecycle stages
- `DRAFT`: user working on application (not validated)
- `REVIEW`: internal review (optional, admin-initiated)
- `SUBMITTED`: sent to government agency
- `APPROVED/REJECTED`: final outcome from agency
- `CANCELLED`: user-initiated or admin-initiated cancellation

---

### 4. Active Application Limits
**Decision:** Enforce limits at API/serializer level (not database constraints)

**Limits:**
- **OSAP:** One active application per academic year (filter by `studyPeriod.endDate`)
- **Passport:** One active application at a time (`status` in `[DRAFT, REVIEW, SUBMITTED]`)
- **SIN/Ontario ID:** No hard limits (users may have multiple in-flight applications for different reasons, e.g., replacement + confirmation)

**Rationale:**
- Business rules may change; easier to adjust in serializer validation than migrations
- Allows admins to override via Django admin if needed
- Clear error messages in API responses

---

### 5. Snapshot Write-Back Policy
**Decision:** Partial write-back from applications to `FoundationalDocumentsSnapshot`

**Rules:**
- **Always write back:** `Address`, `ContactInformation` (assume user's latest info is correct)
- **Conditional write back (with linking documents):** `LegalName`, `dateOfBirth`
  - Only update if application includes `BIRTH_CERT`, `PASSPORT`, or `CITIZENSHIP` document
  - Prevents accidental overwrites from typos
- **Never write back:** `SupportingDocument` (must be explicitly added by user to snapshot)

**Implementation:**
- Triggered after application moves to `APPROVED` status
- Serializer post-save signal or dedicated view action (`POST /api/sin-applications/{id}/sync-to-snapshot/`)

**Rationale:**
- Keeps snapshot fresh with minimal user intervention
- Protects canonical identity fields (name, DOB) from unverified changes
- Addresses/contact change frequently and are low-risk

---

### 6. Data Retention Policy
**Decision:** Keep all historical applications indefinitely (no automatic deletion)

**Justification:**
- Audit trail for government application submissions
- Users may need proof of past applications for appeals or corrections
- Versioning (`version` field) tracks application history

**Future Considerations:**
- Add optional "archive" status for old applications (exclude from default queries)
- Implement soft-delete (`is_archived` boolean) if needed
- Compliance review for PIPEDA (Canada) and data minimization principles

---

### 7. Passport References Modeling
**Decision:** Normalize as `PassportReference` model (not embedded JSONField)

**Rationale:**
- Enforces data integrity (`isFamily=False` constraint)
- Allows admin to view/search references independently
- Simplifies validation (e.g., "guarantor not in references" check)
- M2M relationship makes it easy to query "Which applications used this reference?"

**Trade-offs:**
- More database joins than JSONField
- Requires separate admin registration

---

### 8. Passport Arrays (Addresses, Occupation History)
**Decision:** Hybrid approach

**`addressesLastTwoYears`:** M2M to `Address` model  
- Reuses existing `Address` model
- Allows snapshot pre-fill and deduplication
- Supports address history queries

**`occupationHistory`:** JSONField (array of objects)  
- Lower cardinality (typically 1-3 entries)
- No need for separate `Occupation` model
- Simpler for users (no extra form steps)

**Schema:**
```json
{
  "occupationHistory": [
    {
      "employer": "ABC Corp",
      "position": "Software Engineer",
      "startDate": "2023-01-01",
      "endDate": "2024-12-31"
    }
  ]
}
```

---

### 9. JSON Schema Exposure
**Decision:** Expose via read-only API endpoint

**Endpoint:** `GET /api/schemas/foundational-documents/`  
**Returns:** JSON Schema Draft-07 document (from `core/schemas/foundational_documents.schema.json`)

**Rationale:**
- Enables client-side validation (React forms, mobile app)
- Self-documenting API (clients can introspect application structure)
- Versioned with API (can add `/v2/schemas/...` later)

**Implementation:**
- Simple view in `core/views.py` that loads and returns JSON file
- No authentication required (schema is not sensitive)

---

### 10. Conditional Validation Strategy
**Decision:** Implement in both `Model.clean()` and DRF serializers

**Why Both?**
- **Model clean():** Protects database integrity (enforced even if data comes from admin or scripts)
- **Serializer validation:** Provides better error messages for API clients

**Examples:**
- SIN online → requires proof of address (serializer checks `submittedDocuments`)
- Passport guarantor → must know applicant ≥ 2 years (model `clean()`)
- OSAP dependent → requires parental financials (serializer `validate()`)

**Precedence:** Serializer validation runs first → clearer API errors; model validation is safety net.

---

## Future Decisions (Pending)

### 11. OSAP Financial Data Structure
- [ ] Define schema for `studentFinancials`, `parentalFinancials`, `spousalFinancials` JSONFields
- [ ] Determine which fields require encryption (SINs, income amounts?)
- [ ] Map to OSAP form sections (OSAP 1, OSAP 2, OSAP 3)

### 12. Document Upload/Storage
- [ ] Where to store uploaded supporting documents? (S3, local media, database BLOBs?)
- [ ] How to link uploaded files to `SupportingDocument` records? (FileField vs external URL?)
- [ ] Retention policy for uploaded files (match application retention?)

### 13. Notification/Reminder System
- [ ] When to remind users about incomplete applications? (via Celery task?)
- [ ] How to notify users of status changes? (email, in-app notification, push?)

### 14. Multi-language Support
- [ ] Should application forms support French? (required for federal programs)
- [ ] Translation strategy: gettext, i18n model fields, or client-side?

---

## References
- Session summary: `.chat_notes/session_summary.md`
- JSON Schema: `backend/adultingos_web/core/schemas/foundational_documents.schema.json`
- Models: `backend/adultingos_web/core/models.py`
- Admin: `backend/adultingos_web/core/admin.py`
- Serializers: `backend/adultingos_web/core/serializers.py` (pending)

---

## Change Log
- **2025-11-01:** Initial decisions documented (models, encryption, status, retention, references, schema exposure)
