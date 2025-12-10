# Frontend Auth Pages - Visual Overview

## Page Flow Diagram

```
┌─────────────────┐
│   Landing Page  │
│    (Public)     │
└────────┬────────┘
         │
    ┌────▼─────┐
    │  /login  │◄──────┐
    └────┬─────┘       │
         │             │
    ┌────▼──────┐      │
    │ Register? │      │
    └─┬────────┬┘      │
      │        │       │
      No      Yes      │
      │        │       │
      │   ┌────▼──────────┐
      │   │  /register    │
      │   └────┬──────────┘
      │        │
      │   ┌────▼──────────┐
      │   │ Auto-login or │
      │   │ redirect to / │
      │   └───────────────┘
      │
 ┌────▼──────────┐
 │ Magic Link?   │
 └─┬────────────┬┘
   │            │
  No           Yes
   │            │
   │       ┌────▼────────────┐
   │       │ /auth/verify    │
   │       │ (Request Email) │
   │       └────┬────────────┘
   │            │
   │       ┌────▼────────────┐
   │       │ Email Sent      │
   │       │ Check Inbox     │
   │       └────┬────────────┘
   │            │
   │       ┌────▼────────────────┐
   │       │ Click Link in Email │
   │       └────┬────────────────┘
   │            │
   │       ┌────▼──────────────┐
   │       │ /auth/verify?token│
   │       │ (Auto-verify)     │
   │       └────┬──────────────┘
   │            │
   └────────────┴──────┐
                       │
                  ┌────▼─────┐
                  │    /     │
                  │Dashboard │
                  │(Protected)
                  └────┬─────┘
                       │
                  ┌────▼──────────┐
                  │ Gmail Connect │
                  │   Optional    │
                  └────┬──────────┘
                       │
                  ┌────▼──────────────┐
                  │ /auth/gmail       │
                  │ (OAuth Redirect)  │
                  └────┬──────────────┘
                       │
                  ┌────▼──────────────────┐
                  │ Google OAuth Consent  │
                  └────┬──────────────────┘
                       │
                  ┌────▼─────────────────────┐
                  │ /auth/gmail/callback     │
                  │ (Process & Redirect)     │
                  └────┬─────────────────────┘
                       │
                  ┌────▼─────┐
                  │    /     │
                  │Dashboard │
                  │ (Gmail   │
                  │Connected)│
                  └──────────┘
```

## Page Descriptions

### 1. Login Page (`/login`)

**Layout:**
- Centered card on dark background
- GetAnswers logo and branding at top
- Email input field
- Password input field (toggleable with magic link)
- Primary "Sign In" button
- Divider
- "Request Magic Link" toggle button
- Link to registration
- Terms notice at bottom

**Features:**
- Form validation
- Error messages
- Loading states
- Smooth animations
- Magic link option toggle

**Visual Style:**
- Dark theme (`surface-base` background)
- Gradient logo (cyan to purple)
- Clean, modern form inputs
- Accent cyan for interactive elements

---

### 2. Register Page (`/register`)

**Layout:**
- Centered card on dark background
- GetAnswers logo and branding at top
- Full name input
- Email input
- Password input with strength indicator
- Confirm password input
- Terms checkbox
- Primary "Create Account" button
- Link to login
- Security badge at bottom

**Features:**
- Real-time password strength meter (5 levels)
- Password confirmation matching
- Email format validation
- Name length validation
- Terms acceptance required
- Visual password strength indicator

**Visual Style:**
- Password strength colors: Weak (red) → Fair (orange) → Good (blue) → Strong (green)
- 5-bar strength indicator
- Checkbox for terms acceptance
- Lock icon with "256-bit SSL encryption" badge

---

### 3. Magic Link Page (`/auth/verify`)

**States:**

**A. Request State (Default):**
- Centered card with sparkles icon
- Email input field
- "Send Magic Link" button
- Benefits list explaining why use magic link
- Link back to login

**B. Sent State:**
- Success icon (mail)
- "Check Your Email" message
- Shows email address sent to
- Expiration notice (15 minutes)
- "Use a Different Email" button
- Link back to login

**C. Verifying State (with token in URL):**
- Loading spinner
- "Verifying..." message
- Auto-processes in background

**D. Success State:**
- Green checkmark icon
- "Success!" message
- Auto-redirect countdown

**E. Error State:**
- Red X icon
- Error message
- "Request New Link" button
- Link back to login

---

### 4. Gmail Connect Component

**Two Variants:**

**A. Card Variant** (for settings pages):
- Full card with Gmail branding
- Red-orange gradient Gmail icon
- Connection status indicator
- Feature list (when not connected)
- Active features display (when connected)
- Primary connect/disconnect button
- Security notice

**B. Inline Variant** (for embedded use):
- Minimal layout
- Status badge (if showStatus=true)
- Single connect/disconnect button
- Error display

**Features:**
- Real-time connection status
- OAuth flow handling
- Success/error notifications
- Security information
- Feature benefits explanation

---

### 5. Protected Route (No Visual)

**Behavior:**
- Shows loading spinner while checking auth
- Redirects to `/login` if not authenticated
- Preserves intended destination in state
- Renders children if authenticated

**Loading State:**
- Centered GetAnswers logo
- Spinning loader
- "Loading..." text

---

### 6. Settings Page (Example Usage)

**Sections:**
1. **Profile**
   - User name
   - Email
   - Autonomy level badge

2. **Gmail Integration**
   - GmailConnect component (card variant)

3. **Notifications**
   - Toggle switches for preferences

4. **Privacy & Security**
   - Password change button
   - 2FA button
   - Active sessions button

5. **Danger Zone**
   - Sign out button
   - Delete account button (outlined in red)

---

## Color Scheme

### Surfaces
- `surface-base`: #0a0b0d (main background)
- `surface-elevated`: #111318 (nav/header)
- `surface-card`: #161a22 (cards)
- `surface-hover`: #1c2129 (hover states)
- `surface-border`: #262d3a (borders)

### Status Colors
- `critical`: #ef4444 (red)
- `warning`: #f59e0b (orange)
- `success`: #10b981 (green)
- `info`: #3b82f6 (blue)

### Accents
- `accent-cyan`: #06b6d4
- `accent-purple`: #8b5cf6

### Text
- `text-primary`: #f1f5f9 (main text)
- `text-secondary`: #94a3b8 (secondary text)
- `text-muted`: #64748b (muted text)

---

## Component Reusability

### Input Component
```tsx
<Input
  label="Email"
  type="email"
  placeholder="you@company.com"
  error="Email is required"
  helperText="We'll never share your email"
/>
```

### Button Component
```tsx
<Button
  variant="primary"  // or secondary, outline, ghost, danger
  size="lg"         // or sm, md
  isLoading={true}
  icon={<Mail className="w-4 h-4" />}
>
  Send Email
</Button>
```

---

## Animations

All pages use Framer Motion for:

1. **Page Entry**
   - Fade in from 0 to 1 opacity
   - Slide up 20px
   - Duration: 400ms

2. **Form Errors**
   - Slide down from -10px
   - Fade in

3. **Buttons**
   - Scale 1.02 on hover
   - Scale 0.98 on tap

4. **Success/Error Messages**
   - Fade and slide animations
   - Exit animations

5. **Loading Spinners**
   - Smooth rotation
   - Consistent timing

---

## Mobile Responsiveness

All auth pages are responsive:

- **Mobile (< 640px)**
  - Full width forms with padding
  - Single column layout
  - Touch-friendly button sizes
  - Optimized font sizes

- **Tablet (640px - 1024px)**
  - Centered cards with max-width
  - Comfortable spacing
  - Readable text sizes

- **Desktop (> 1024px)**
  - Centered cards (max-width: 28rem/448px)
  - Hover effects active
  - Full animation suite

---

## Accessibility

- Proper ARIA labels
- Keyboard navigation support
- Focus indicators (cyan outline)
- Screen reader friendly
- Semantic HTML
- Form field associations
- Error announcements

---

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

Requires modern CSS features:
- CSS Grid
- Flexbox
- CSS Variables
- Transform/Transitions
