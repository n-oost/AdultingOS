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

## Current Session Work
### Environment Setup
- Configured Python environment for the project.
- Installed Django and other required packages from `requirements.txt`.
- Successfully ran all tests and API tests.

### Test Planning
- Reviewed existing test files (`backend/adultingos_web/core/tests.py`, `backend/tests/test_utils.py`) and core application files (`models.py`, `views.py`, `serializers.py`).
- Created a detailed to-do list for improving test coverage across serializers and viewsets.
- Started implementing tests for `TaskSerializer` and `TagSerializer` in `backend/adultingos_web/core/test_serializers.py`.

## Next Steps (From Todo List)
1. **Write tests for TaskSerializer and TagSerializer**
   - Add tests for creating, updating, and validating tasks and tags via their serializers.
2. **Write tests for user auth serializers**
   - Test user registration with valid data, password mismatches, and existing usernames. Test user login with correct and incorrect credentials.
3. **Write tests for UserProfileSerializer**
   - Add tests for creating and updating a UserProfile.
4. **Write tests for TaskViewSet**
   - Test the CRUD operations for the TaskViewSet, including filtering by status, category, and search. Test the custom actions `mark_complete` and `mark_incomplete`.
5. **Write tests for TagViewSet**
   - Test the CRUD operations for the TagViewSet.
6. **Write tests for auth views**
   - Test the `register` and `login_view` API endpoints to ensure they handle success and error cases correctly.
7. **Write tests for UserProfileViewSet**
   - Test fetching and updating user profiles via the `UserProfileViewSet`.
8. **Write tests for Application ViewSets**
   - Add tests for all the application ViewSets: SIN, Passport, Ontario ID, and OSAP.

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

