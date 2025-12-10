# GetAnswers Frontend Authentication

Complete authentication system for the GetAnswers AI email management platform.

## Features Implemented

### 1. Authentication Pages

#### Login Page (`/login`)
- Email and password authentication
- Magic link option (passwordless login)
- Form validation with error messages
- Loading states and smooth animations
- Link to registration page
- Responsive design with dark theme

#### Register Page (`/register`)
- User registration with name, email, and password
- Real-time password strength indicator
- Password confirmation validation
- Terms and conditions acceptance
- Comprehensive form validation
- Auto-redirect after successful registration

#### Magic Link Page (`/auth/verify`)
- Request magic link via email
- Email verification with token
- Success and error states
- Automatic redirect after verification
- Security benefits explanation

### 2. Protected Routes

#### ProtectedRoute Component
- Wrapper for authenticated-only pages
- Automatic authentication check on mount
- Loading state while checking auth
- Redirect to login if not authenticated
- Preserves intended destination URL

### 3. Gmail Integration

#### GmailConnect Component
- OAuth 2.0 connection flow
- Two variants: `card` and `inline`
- Connection status display
- Disconnect functionality
- Success/error notifications
- Feature list for non-connected users

#### Gmail Callback Handler
- Processes OAuth callback
- Handles authorization codes
- Error handling for denied access
- Redirects to main app with status

### 4. Authentication Store

Zustand-based state management with:
- User authentication state
- Login/logout functionality
- Registration
- Magic link requests and verification
- Gmail OAuth handling
- Persistent authentication checking
- Error handling

## File Structure

```
frontend/src/
├── components/
│   ├── auth/
│   │   ├── LoginPage.tsx           # Login form
│   │   ├── RegisterPage.tsx        # Registration form
│   │   ├── MagicLinkPage.tsx       # Magic link request/verify
│   │   ├── ProtectedRoute.tsx      # Route protection wrapper
│   │   ├── GmailConnect.tsx        # Gmail OAuth integration
│   │   └── GmailCallbackPage.tsx   # OAuth callback handler
│   ├── ui/
│   │   ├── Input.tsx               # Form input component
│   │   └── Button.tsx              # Button component
│   ├── settings/
│   │   └── SettingsPage.tsx        # Settings page example
│   └── dashboard/
│       └── Dashboard.tsx           # Main app dashboard
├── stores/
│   └── authStore.ts                # Authentication state management
└── App.tsx                         # Updated with routing

```

## Routes

| Route | Component | Protected | Description |
|-------|-----------|-----------|-------------|
| `/` | Dashboard | Yes | Main application dashboard |
| `/login` | LoginPage | No | Login page |
| `/register` | RegisterPage | No | Registration page |
| `/auth/verify` | MagicLinkPage | No | Magic link verification |
| `/auth/gmail/callback` | GmailCallbackPage | No | Gmail OAuth callback |

## Setup Instructions

### 1. Install Dependencies

```bash
cd frontend
npm install react-router-dom
```

### 2. Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:3000/api
```

### 3. Run the Development Server

```bash
npm run dev
```

## Usage Examples

### Using Protected Routes

```tsx
import { ProtectedRoute } from './components/auth/ProtectedRoute';

<Route
  path="/dashboard"
  element={
    <ProtectedRoute>
      <Dashboard />
    </ProtectedRoute>
  }
/>
```

### Using Gmail Connect (Card Variant)

```tsx
import { GmailConnect } from './components/auth/GmailConnect';

<GmailConnect
  variant="card"
  showStatus={true}
  onSuccess={() => console.log('Gmail connected!')}
  onError={(error) => console.error(error)}
/>
```

### Using Gmail Connect (Inline Variant)

```tsx
<GmailConnect
  variant="inline"
  showStatus={true}
/>
```

### Accessing Auth State

```tsx
import { useAuthStore } from './stores/authStore';

function MyComponent() {
  const { user, isAuthenticated, login, logout } = useAuthStore();

  // Use auth state and methods
}
```

## API Integration

The auth store expects these backend endpoints:

### Authentication Endpoints

- `POST /api/auth/login` - Login with email/password
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```

- `POST /api/auth/register` - Register new user
  ```json
  {
    "name": "John Doe",
    "email": "user@example.com",
    "password": "password123"
  }
  ```

- `POST /api/auth/magic-link` - Request magic link
  ```json
  {
    "email": "user@example.com"
  }
  ```

- `GET /api/auth/verify?token=xxx` - Verify magic link token

- `POST /api/auth/logout` - Logout user

- `GET /api/auth/me` - Get current user (with cookies)

### Gmail OAuth Endpoints

- `GET /api/auth/gmail` - Initiate Gmail OAuth flow (redirects)

- `GET /api/auth/gmail/callback?code=xxx` - Handle OAuth callback

- `POST /api/auth/gmail/disconnect` - Disconnect Gmail

## Component Props

### Input Component

```tsx
interface InputProps {
  label?: string;
  error?: string;
  helperText?: string;
  // ...standard HTML input props
}
```

### Button Component

```tsx
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  icon?: React.ReactNode;
  // ...standard HTML button props
}
```

### GmailConnect Component

```tsx
interface GmailConnectProps {
  onSuccess?: () => void;
  onError?: (error: string) => void;
  variant?: 'card' | 'inline';
  showStatus?: boolean;
}
```

## Design System

### Colors (from theme)

- **Surface Colors**: `surface-base`, `surface-elevated`, `surface-card`, `surface-hover`
- **Text Colors**: `text-primary`, `text-secondary`, `text-muted`
- **Status Colors**: `success`, `warning`, `critical`, `info`
- **Accent Colors**: `accent-cyan`, `accent-purple`

### Typography

- **Font Family**: Plus Jakarta Sans (body), JetBrains Mono (code)
- **Headings**: `text-3xl`, `text-2xl`, `text-xl`
- **Body**: `text-base`, `text-sm`, `text-xs`

### Spacing & Layout

- **Padding**: `p-6`, `p-8` (for cards)
- **Gaps**: `gap-3`, `gap-4`, `gap-6`
- **Border Radius**: `rounded-lg`, `rounded-xl`, `rounded-2xl`

## Security Features

1. **CSRF Protection**: All requests include credentials
2. **OAuth 2.0**: Secure Gmail authentication
3. **Magic Links**: Passwordless authentication option
4. **Password Validation**: Strong password requirements
5. **Form Validation**: Client-side validation before submission
6. **Error Handling**: Comprehensive error messages

## Responsive Design

All auth pages are fully responsive:
- Mobile: Single column, optimized touch targets
- Tablet: Centered layout with max-width
- Desktop: Full experience with smooth animations

## Animations

Using Framer Motion for:
- Page transitions (fade in, slide up)
- Button hover/tap effects
- Loading spinners
- Success/error message animations
- Card hover effects

## Next Steps

To complete the authentication system:

1. **Backend Integration**: Implement the API endpoints listed above
2. **Email Service**: Set up email delivery for magic links
3. **OAuth Configuration**: Configure Google OAuth credentials
4. **Session Management**: Implement JWT or session-based auth
5. **Password Reset**: Add forgot password flow
6. **2FA**: Add two-factor authentication option
7. **Social Auth**: Add more OAuth providers (Microsoft, etc.)

## Testing

Test the auth flow:

1. Navigate to `/register` and create an account
2. Try logging in with email/password at `/login`
3. Request a magic link and verify email flow
4. Test protected route access
5. Connect Gmail account
6. Verify logout functionality

## Troubleshooting

### Routes not working
- Make sure `react-router-dom` is installed
- Check that `BrowserRouter` wraps the app

### Auth state not persisting
- Check browser localStorage for `auth-storage`
- Verify API returns proper user data

### Gmail OAuth not working
- Verify OAuth redirect URIs in Google Console
- Check API endpoint configuration
- Ensure callback URL matches exactly

## Support

For questions or issues:
- Check the component source code
- Review the API integration section
- Test with mock data first
