/**
 * ProfileForm.jsx
 *
 * A component for viewing and editing the user's profile.
 * - Fetches profile data using profile.get()
 * - Allows editing and saving with profile.update()
 * - Shows loading and error states
 */

import React, { useState, useEffect } from 'react';
import { profile } from '../services/apiService';

export default function ProfileForm() {
  // Profile data state
  const [profileData, setProfileData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  // Form fields
  const [age, setAge] = useState('');
  const [occupation, setOccupation] = useState('');
  const [isStudent, setIsStudent] = useState(false);
  const [filingStatus, setFilingStatus] = useState('');
  const [hasDependents, setHasDependents] = useState(false);
  const [dependentCount, setDependentCount] = useState(0);
  const [has401k, setHas401k] = useState(false);
  const [hasHsa, setHasHsa] = useState(false);
  const [isHomeowner, setIsHomeowner] = useState(false);
  const [hasStudentLoans, setHasStudentLoans] = useState(false);
  const [hasHealthInsurance, setHasHealthInsurance] = useState(false);

  // Load profile on mount
  useEffect(() => {
    loadProfile();
  }, []);

  async function loadProfile() {
    try {
      setError('');
      setLoading(true);
      const data = await profile.get();
      setProfileData(data);
      
      // Populate form fields
      setAge(data.age || '');
      setOccupation(data.occupation || '');
      setIsStudent(data.is_student || false);
      setFilingStatus(data.filing_status || '');
      setHasDependents(data.has_dependents || false);
      setDependentCount(data.dependent_count || 0);
      setHas401k(data.has_401k || false);
      setHasHsa(data.has_hsa || false);
      setIsHomeowner(data.is_homeowner || false);
      setHasStudentLoans(data.has_student_loans || false);
      setHasHealthInsurance(data.has_health_insurance || false);
    } catch (err) {
      setError(err?.message || 'Failed to load profile');
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setSuccessMessage('');
    setSaving(true);

    try {
      const updates = {
        age: age ? parseInt(age) : null,
        occupation: occupation || null,
        is_student: isStudent,
        filing_status: filingStatus || null,
        has_dependents: hasDependents,
        dependent_count: dependentCount,
        has_401k: has401k,
        has_hsa: hasHsa,
        is_homeowner: isHomeowner,
        has_student_loans: hasStudentLoans,
        has_health_insurance: hasHealthInsurance,
      };

      await profile.update(updates);
      setSuccessMessage('Profile updated successfully!');
      await loadProfile(); // Refresh to get updated data
    } catch (err) {
      setError(err?.message || 'Failed to update profile');
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return <div style={{ padding: 20 }}>Loading profile...</div>;
  }

  if (!profileData) {
    return <div style={{ padding: 20, color: '#b00020' }}>Unable to load profile</div>;
  }

  return (
    <div style={{ maxWidth: 600, margin: '20px auto', padding: 20 }}>
      <h2>Your Profile</h2>
      <p style={{ color: '#666', fontSize: 14, marginBottom: 20 }}>
        Profile completeness: {profileData.profile_completeness}%
      </p>

      {/* Success message */}
      {successMessage && (
        <div style={{ background: '#d4edda', color: '#155724', padding: 12, borderRadius: 6, marginBottom: 12 }}>
          {successMessage}
        </div>
      )}

      {/* Error message */}
      {error && (
        <div style={{ background: '#fdecea', color: '#b00020', padding: 12, borderRadius: 6, marginBottom: 12 }}>
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        {/* Basic Information */}
        <fieldset style={{ border: '1px solid #ddd', borderRadius: 6, padding: 16, marginBottom: 16 }}>
          <legend>Basic Information</legend>

          <label htmlFor="age" style={{ display: 'block', marginBottom: 8 }}>
            Age
            <input
              id="age"
              type="number"
              value={age}
              onChange={(e) => setAge(e.target.value)}
              placeholder="Your age"
              style={{ width: '100%', padding: 8, marginTop: 4 }}
            />
          </label>

          <label htmlFor="occupation" style={{ display: 'block', marginBottom: 8 }}>
            Occupation
            <input
              id="occupation"
              type="text"
              value={occupation}
              onChange={(e) => setOccupation(e.target.value)}
              placeholder="Your occupation"
              style={{ width: '100%', padding: 8, marginTop: 4 }}
            />
          </label>

          <label style={{ display: 'flex', alignItems: 'center', marginBottom: 8 }}>
            <input
              type="checkbox"
              checked={isStudent}
              onChange={(e) => setIsStudent(e.target.checked)}
              style={{ marginRight: 8 }}
            />
            I am a student
          </label>
        </fieldset>

        {/* Tax & Financial */}
        <fieldset style={{ border: '1px solid #ddd', borderRadius: 6, padding: 16, marginBottom: 16 }}>
          <legend>Tax & Financial</legend>

          <label htmlFor="filingStatus" style={{ display: 'block', marginBottom: 8 }}>
            Filing Status
            <select
              id="filingStatus"
              value={filingStatus}
              onChange={(e) => setFilingStatus(e.target.value)}
              style={{ width: '100%', padding: 8, marginTop: 4 }}
            >
              <option value="">Select status</option>
              <option value="single">Single</option>
              <option value="married_joint">Married Filing Jointly</option>
              <option value="married_separate">Married Filing Separately</option>
              <option value="head_of_household">Head of Household</option>
            </select>
          </label>

          <label style={{ display: 'flex', alignItems: 'center', marginBottom: 8 }}>
            <input
              type="checkbox"
              checked={hasDependents}
              onChange={(e) => {
                setHasDependents(e.target.checked);
                if (!e.target.checked) setDependentCount(0);
              }}
              style={{ marginRight: 8 }}
            />
            I have dependents
          </label>

          {hasDependents && (
            <label htmlFor="dependentCount" style={{ display: 'block', marginBottom: 8, marginLeft: 24 }}>
              Number of dependents
              <input
                id="dependentCount"
                type="number"
                min="0"
                value={dependentCount}
                onChange={(e) => setDependentCount(parseInt(e.target.value) || 0)}
                style={{ width: '100%', padding: 8, marginTop: 4 }}
              />
            </label>
          )}

          <label style={{ display: 'flex', alignItems: 'center', marginBottom: 8 }}>
            <input
              type="checkbox"
              checked={has401k}
              onChange={(e) => setHas401k(e.target.checked)}
              style={{ marginRight: 8 }}
            />
            I have a 401(k)
          </label>

          <label style={{ display: 'flex', alignItems: 'center', marginBottom: 8 }}>
            <input
              type="checkbox"
              checked={hasHsa}
              onChange={(e) => setHasHsa(e.target.checked)}
              style={{ marginRight: 8 }}
            />
            I have an HSA
          </label>
        </fieldset>

        {/* Life Circumstances */}
        <fieldset style={{ border: '1px solid #ddd', borderRadius: 6, padding: 16, marginBottom: 16 }}>
          <legend>Life Circumstances</legend>

          <label style={{ display: 'flex', alignItems: 'center', marginBottom: 8 }}>
            <input
              type="checkbox"
              checked={isHomeowner}
              onChange={(e) => setIsHomeowner(e.target.checked)}
              style={{ marginRight: 8 }}
            />
            I am a homeowner
          </label>

          <label style={{ display: 'flex', alignItems: 'center', marginBottom: 8 }}>
            <input
              type="checkbox"
              checked={hasStudentLoans}
              onChange={(e) => setHasStudentLoans(e.target.checked)}
              style={{ marginRight: 8 }}
            />
            I have student loans
          </label>

          <label style={{ display: 'flex', alignItems: 'center', marginBottom: 8 }}>
            <input
              type="checkbox"
              checked={hasHealthInsurance}
              onChange={(e) => setHasHealthInsurance(e.target.checked)}
              style={{ marginRight: 8 }}
            />
            I have health insurance
          </label>
        </fieldset>

        <div style={{ display: 'flex', gap: 12 }}>
          <button 
            type="submit" 
            disabled={saving}
            style={{ 
              flex: 1, 
              padding: 12, 
              background: '#2563eb', 
              color: 'white', 
              border: 'none', 
              borderRadius: 6,
              cursor: saving ? 'not-allowed' : 'pointer',
              opacity: saving ? 0.6 : 1
            }}
          >
            {saving ? 'Saving...' : 'Save Profile'}
          </button>
          
          <button
            type="button"
            onClick={loadProfile}
            disabled={loading || saving}
            style={{
              padding: 12,
              background: '#f3f4f6',
              border: '1px solid #d1d5db',
              borderRadius: 6,
              cursor: (loading || saving) ? 'not-allowed' : 'pointer'
            }}
          >
            Reset
          </button>
        </div>
      </form>

      <p style={{ fontSize: 12, color: '#666', marginTop: 16 }}>
        Last updated: {new Date(profileData.last_profile_update).toLocaleString()}
      </p>
    </div>
  );
}
