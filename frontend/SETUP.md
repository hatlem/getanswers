# GetAnswers Frontend - Quick Setup

## Installation

1. **Install dependencies** (including react-router-dom):
   ```bash
   npm install react-router-dom
   ```

2. **Set environment variables**:
   Create a `.env` file:
   ```env
   VITE_API_URL=http://localhost:3000/api
   ```

3. **Run the development server**:
   ```bash
   npm run dev
   ```

## What's Included

### Authentication System
- Login page with password or magic link
- Registration page with validation
- Protected routes
- Gmail OAuth integration
- Auth state management

### Routes
- `/login` - Login page
- `/register` - Registration page
- `/auth/verify` - Magic link verification
- `/auth/gmail/callback` - Gmail OAuth callback
- `/` - Main dashboard (protected)

### Components Created
```
src/components/
├── auth/
│   ├── LoginPage.tsx
│   ├── RegisterPage.tsx
│   ├── MagicLinkPage.tsx
│   ├── ProtectedRoute.tsx
│   ├── GmailConnect.tsx
│   └── GmailCallbackPage.tsx
├── ui/
│   ├── Input.tsx
│   └── Button.tsx
└── settings/
    └── SettingsPage.tsx (example usage)
```

## Testing the Auth Flow

1. Start the dev server
2. Navigate to `http://localhost:5173/login`
3. Try registering a new account at `/register`
4. Test the magic link flow
5. Access the protected dashboard at `/`

## Backend Integration Needed

The frontend expects these API endpoints:
- `POST /api/auth/login` - Login
- `POST /api/auth/register` - Register
- `POST /api/auth/magic-link` - Request magic link
- `GET /api/auth/verify?token=xxx` - Verify magic link
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - Logout
- `GET /api/auth/gmail` - Start Gmail OAuth
- `GET /api/auth/gmail/callback` - Handle OAuth callback
- `POST /api/auth/gmail/disconnect` - Disconnect Gmail

See `FRONTEND_AUTH_README.md` for full documentation.
