# Quick Start: Profile Dropdown and Auth Page UI Enhancement

**Feature**: 012-profile-dropdown-ui
**Branch**: `012-profile-dropdown-ui`

## Overview

This guide provides step-by-step instructions for implementing the profile dropdown menu and auth page UI improvements.

## Prerequisites

- Frontend dev server running (`npm run dev`)
- Existing Navbar component
- User authentication system in place
- Tailwind CSS configured

## Component Overview

### 1. ProfileDropdown Component

**Location**: `frontend/components/ProfileDropdown.tsx`

**Key Features**:
- Clickable profile picture or default icon
- Dropdown menu with logout option
- Click-outside detection
- Keyboard accessible (Tab, Enter, Escape)

### 2. Footer Component

**Location**: `frontend/components/Footer.tsx`

**Content**:
- Terms of Service link
- Privacy Policy link
- Copyright notice

### 3. Updated Navbar

**Location**: `frontend/components/Navbar.tsx`

**Changes**:
- Removed standalone logout button
- Integrated ProfileDropdown component
- Fixed username display logic

### 4. Enhanced Auth Page

**Location**: `frontend/app/auth/page.tsx`

**Improvements**:
- Added navbar at top
- Added footer at bottom
- Centered Google OAuth button
- Improved spacing and alignment

## Implementation Steps

### Step 1: Create Helper Function

Create `frontend/lib/utils/getUserDisplayName.ts`:
- Extract full name from oauth_data JSON
- Fallback to username if no name available
- Truncate long names (>20 chars)

### Step 2: Build ProfileDropdown Component

1. Create component with profile picture/icon trigger
2. Add dropdown menu with logout button
3. Implement click-outside detection
4. Add keyboard handlers (Escape closes dropdown)
5. Add accessibility attributes (ARIA roles)

### Step 3: Update Navbar Component

1. Import ProfileDropdown
2. Remove standalone logout button section
3. Replace with ProfileDropdown component
4. Pass user data and signOut handler

### Step 4: Create Footer Component

1. Create simple footer with links
2. Style with Tailwind (dark theme)
3. Make responsive for mobile

### Step 5: Enhance Auth Page

1. Import Navbar and Footer components
2. Add Navbar at top of page (before auth form)
3. Add Footer at bottom (after form)
4. Fix Google OAuth button width and alignment
5. Add smooth transitions to form elements

## Testing Checklist

- [ ] Click profile picture → dropdown opens
- [ ] Click "Logout" in dropdown → user logged out
- [ ] Click outside dropdown → dropdown closes
- [ ] Press Escape → dropdown closes
- [ ] Google OAuth users see profile picture
- [ ] Email/password users see default icon
- [ ] Username shows correctly (not email)
- [ ] Auth page has navbar matching other pages
- [ ] Auth page has footer with links
- [ ] "Sign in with Google" button is centered
- [ ] All hover states work smoothly
- [ ] Works on mobile devices

## Troubleshooting

**Issue**: Dropdown doesn't close on outside click
- **Solution**: Check click event listener is attached to document, verify ref is pointing to dropdown element

**Issue**: Profile picture not showing
- **Solution**: Verify oauth_data contains picture URL, check onError handler

**Issue**: Username showing email instead of name
- **Solution**: Check getUserDisplayName logic, verify oauth_data parsing

**Issue**: Auth page navbar looks different
- **Solution**: Ensure using same Navbar component, check conditional rendering logic

## Code Patterns

### Dropdown State Management
```typescript
const [isOpen, setIsOpen] = useState(false);
const dropdownRef = useRef<HTMLDivElement>(null);

// Toggle dropdown
const toggleDropdown = () => setIsOpen(!isOpen);

// Close on outside click
useClickOutside(dropdownRef, () => setIsOpen(false));

// Close on Escape
useEffect(() => {
  const handleEscape = (e: KeyboardEvent) => {
    if (e.key === 'Escape') setIsOpen(false);
  };
  document.addEventListener('keydown', handleEscape);
  return () => document.removeEventListener('keydown', handleEscape);
}, []);
```

### Profile Picture with Fallback
```typescript
{user.profile_picture ? (
  <img
    src={user.profile_picture}
    alt="Profile"
    className="w-8 h-8 rounded-full"
    onError={(e) => {
      e.currentTarget.style.display = 'none';
      // Show fallback icon
    }}
  />
) : (
  <User className="w-5 h-5" />
)}
```

### Username Extraction
```typescript
function getUserDisplayName(user: User): string {
  // Try Google profile name
  if (user.auth_provider === 'google' && user.oauth_data) {
    const data = JSON.parse(user.oauth_data);
    if (data.name) return data.name;
  }

  // Fallback to username
  return user.username;
}
```

## Next Steps

After implementing and testing:
1. Commit changes with descriptive message
2. Create pull request (if using Git workflow)
3. Consider extracting dropdown logic into reusable hook
4. Plan additional dropdown menu items for future (Profile, Settings)
