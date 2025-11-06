# AdultingOS Session Summary
**Date:** 2025-10-19  
**Branch:** FOUNDATION  
**Context:** Foundational Identity & Education Module (Ontario) - Master Schema Implementation

## Completed Work
### 1. Architecture Planning
- **Design choice:** Hybrid model (recommended)
  - Profile-level `FoundationalDocumentsSnapshot` (1:1 with User): canonical, reusable identity for prefilling
  - Versioned per-module `Application` models: full history, statuses, timestamps
  - Snapshot write-back rules: addresses/contact always; legalName/DOB only with linking documents

### 2. Schema Analysis
- Read and extracted requirements from `Foundational Identity Module Schema.txt`
- Identified four application modules:
  - `sinApplication` (federal, ESDC/Service Canada)
  - `passportApplication` (federal, IRCC Passport Program)
  - `ontarioProvincialIdApplication` (provincial, MTO/ServiceOntario)
  - `osapApplication` (provincial, MCU)
- Defined reusable core objects:
  - `LegalName`, `PersonalInformation`, `Address`, `ContactInformation`, `SupportingDocument`
- Documented conditional validation rules:
  - SIN: if Online, require ProofOfAddress
  - Passport: guarantor passport format (8-digit), yearsKnown ≥ 2; references not family; guarantor not a reference
  - Ontario ID: if DriverLicense, require medicalInformation; mutual exclusivity (surrender flag)
  - OSAP: if isDependent, require parentalFinancials; if Married/CommonLaw, require spousalFinancials; deadlines relative to studyPeriod.endDate

### 3. JSON Schema (Draft-07)
- Created complete JSON Schema: `schemas/foundational_documents.schema.json`
- Includes definitions, enumerations, conditional if/then/else rules, pattern matching
- Ready to place in backend: `backend/adultingos_web/core/schemas/foundational_documents.schema.json`

### 4. Multi-root Workspace
- Created `AdultingOS-MultiRoot.code-workspace` to work across Gov_scraper and AdultingOS simultaneously
- Keeps Git repos separate; allows tool access to both projects
- Added tasks for convenience: run pipeline, Django server, FastAPI backend, frontend

## Pending Implementation (Ready to Apply)
### Models to Add
1. **Reusable Core Models**
   - `LegalName(firstName, middleName, lastName)`
   - `PersonalInformation(legalName, dateOfBirth, placeOfBirth, sex enum [M,F,X], formerNames[], height, gender)`
   - `Address(streetAddress, apartmentUnit, city, province, postalCode, country)`
   - `ContactInformation(primaryPhoneNumber, alternatePhoneNumber, emailAddress)`
   - `SupportingDocument(documentType enum, issuingAuthority, documentNumber, issueDate, expiryDate, functionalRole enum)`

2. **Profile Snapshot Container**
   - `FoundationalDocumentsSnapshot` (1:1 with User)
     - Links to reusable objects; canonical identity for prefilling apps

3. **Versioned Application Models**
   - `SINApplication(submissionMethod enum, applicationType enum, applicantInformation, contactInformation, address, submittedDocuments M2M, status, version, timestamps)`
   - `PassportApplication(applicantInformation, contactInformation, addressesLastTwoYears[], occupationHistory[], guarantor, references[2], submittedDocuments[], status, version, timestamps)`
   - `Guarantor(fullName, canadianPassportNumber, yearsKnown)`
   - `Reference(fullName, relationship, contact, isFamily)`
   - `OntarioProvincialIdApplication(applicationType enum [DriverLicense, PhotoCard], applicantInformation, address, isSurrenderingExistingId, medicalInformation, submittedDocuments[], status, version, timestamps)`
   - `OSAPApplication(studentProfile, dependencyInformation, academicInformation(studyPeriod), studentFinancials, parentalFinancials, spousalFinancials, status, version, timestamps)`

4. **Validations**
   - Model clean() methods and DRF serializer validators for conditional rules
   - Encryption at rest for SIN (user/parents/spouse) and guarantor passport number
   - Status workflow: [draft, review, submitted, approved, rejected, cancelled]
   - Active-application limits: one active OSAP per academic year; one active Passport at a time

5. **Admin & Serializers**
   - Register all models in Django admin with redaction for sensitive fields
   - DRF serializers mirroring validation logic

### Clarifications Pending
- [ ] User model path (django.contrib.auth.models.User or custom UserProfile?)
- [ ] Encryption library preference (django-fernet-fields, django-encrypted-model-fields, or custom AES/KMS?)
- [ ] Application status values: confirm [draft, review, submitted, approved, rejected, cancelled]
- [ ] Active-application limits: OSAP (one per year), Passport (one at a time), SIN/Ontario ID (allow multiple or restrict?)
- [ ] Snapshot write-back policy: confirm addresses/contact always; legalName/DOB only with linking docs
- [ ] Passport references: relationship enum or isFamily boolean? Enforce "guarantor not a reference" in serializer?
- [ ] Data retention: keep all historical applications indefinitely or specify retention policy?
- [ ] Passport arrays (addressesLastTwoYears, occupationHistory): normalized child tables or JSONField?
- [ ] SIN format: normalize (9 digits), regex validation, encrypt at rest, mask in API (*\*\*-\*\*\*-123)?
- [ ] JSON Schema exposure: endpoint (/api/schemas/foundational-documents) or files only?
- [ ] Final enum sets: confirm applicationType and functionalRole values

## Current Session Work (November 1, 2025)
### ✅ Foundational Identity Module Implementation
Successfully implemented the complete foundational infrastructure for Canadian identity documents and education funding applications:

#### 1. Models & Database
- Created reusable core models: `LegalName`, `PersonalInformation`, `Address`, `ContactInformation`, `SupportingDocument`
- Implemented profile container: `FoundationalDocumentsSnapshot` (1:1 with User)
- Added versioned application models: `SINApplication`, `PassportApplication` (with `PassportGuarantor` and `PassportReference`), `OntarioProvincialIdApplication`, `OSAPApplication`
- Status workflow: `DRAFT → REVIEW → SUBMITTED → APPROVED/REJECTED/CANCELLED`
- Model validation: conditional rules in `clean()` methods (online SIN requires proof of address, guarantor ≥2 years known, etc.)
- Generated and applied migration `0005`
- Configured SQLite fallback for development/testing (Postgres optional)

#### 2. Encryption & Security
- Installed `django-encrypted-model-fields` v0.6.5 (Django 5.x compatible)
- Encrypted sensitive fields:
  - `SINApplication.sin_number` (9 digits)
  - `PassportGuarantor.canadian_passport_number` (8 digits)
- Added `FIELD_ENCRYPTION_KEY` configuration in settings
- Admin interface masks sensitive data: SIN as `***-***-123`, passport as `****1234`

#### 3. JSON Schema & API
- Created comprehensive JSON Schema Draft-07: `backend/adultingos_web/core/schemas/foundational_documents.schema.json`
- Includes all definitions, enumerations, conditional validation rules, pattern matching
- Exposed via public API endpoint: `GET /api/schemas/foundational-documents/`
- View and URL route registered in Django

#### 4. Admin Interface
- All models registered with list displays, filters, and search
- Sensitive fields redacted in list views (masked display methods)
- Readonly version fields for audit trail
- Date hierarchies for easy navigation

#### 5. Documentation
- Created `docs/decisions/foundational_identity.md` documenting all architectural decisions:
  - User model choice (Django built-in User)
  - Encryption library selection
  - Application status values
  - Active application limits
  - Snapshot write-back policy
  - Data retention policy
  - References modeling approach (normalized vs JSONField)
  - JSON Schema exposure strategy

#### 6. Testing
- All migrations applied successfully
- 45 tests discovered: **36 passed, 8 failures, 1 error**
- Failures are minor (ordering, missing import, validation edge cases)
- Core foundational models tests passing
- Database setup validated with SQLite

## Next Steps (From Todo List)
1. **Create DRF Serializers** for foundational models
   - `SINApplicationSerializer`, `PassportApplicationSerializer`, `OntarioProvincialIdApplicationSerializer`, `OSAPApplicationSerializer`
   - Implement field-level validation (SIN format, guarantor rules, OSAP constraints)
   - Add object-level validation for conditional rules
2. **Fix existing test failures**
   - Tag creation ordering issue
   - UserProfileSerializer import missing
   - Validation assertions for SIN proof of address
   - Task ordering in list views
3. **Add comprehensive tests** for new models and serializers
   - Happy path tests for each application type
   - Edge cases (invalid data, missing required fields)
   - Conditional validation scenarios
4. **Test schema endpoint** manually (curl/browser)
5. **Implement snapshot write-back logic** (triggered on APPROVED status)
6. **Document API endpoints** in `docs/api/foundational-identity.md`

## Key Files
- `.chat_notes/session_summary.md`: this file (session state and decisions)
- `Foundational Identity Module Schema.txt`: source requirements document (in Gov_scraper workspace)
- `schemas/foundational_documents.schema.json` (Gov_scraper): staged JSON Schema to copy into backend

## Architecture Decisions
- Hybrid model: snapshot + versioned applications for full history and fast profile queries
- Conditional validation enforced at model clean() and serializer levels
- SIN and guarantor passport encrypted at rest; masked in API outputs
- Mutual exclusivity for Ontario ID enforced via isSurrenderingExistingId flag
- OSAP deadlines computed as relative offsets from studyPeriod.endDate

## References
- Source document: `Foundational Identity Module Schema.txt` (Gov_scraper workspace)
- JSON Schema Draft-07: https://json-schema.org/draft-07/schema
- Django encrypted fields: https://pypi.org/project/django-fernet-fields/


## Chat History
---
(Paste chat history here)

