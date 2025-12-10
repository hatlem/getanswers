# GetAnswers Frontend API Client & React Query Hooks

Complete implementation of the frontend API client and React Query hooks for the GetAnswers project.

## Overview

This implementation provides a type-safe, production-ready API client with React Query integration for optimal data fetching, caching, and state management.

## Architecture

### State Management Strategy

**React Query** handles server state:
- Queue items
- Statistics
- Conversations
- User data from API

**Zustand** handles UI state:
- Active view/filter
- Selected card/conversation
- UI preferences (persisted to localStorage)

## Files Created

### Core API Client

#### `/frontend/src/lib/api.ts`
- Base HTTP client with automatic token injection
- 401 handling with automatic redirect to login
- Type-safe request/response handling
- Error transformation to ApiError class
- Organized API endpoints by domain

**Key Features:**
- Configurable base URL from `VITE_API_BASE_URL` env variable
- JWT token management via localStorage
- Automatic Authorization header injection
- Response interceptors for error handling
- Handles empty responses (204 No Content)

### React Query Setup

#### `/frontend/src/lib/queryClient.ts`
- Configured QueryClient with sensible defaults
- Query key factory for consistent cache keys
- Automatic retry logic with exponential backoff
- Stale time: 30 seconds for queries
- Cache time: 5 minutes before garbage collection

### React Query Hooks

#### `/frontend/src/hooks/useAuth.ts`
Authentication hooks with automatic cache invalidation:

- `useCurrentUser()` - Fetch current user (auto-retry disabled on 401)
- `useLogin()` - Login mutation with cache update
- `useRegister()` - Registration mutation
- `useLogout()` - Logout with cache clearing
- `useRequestMagicLink()` - Request magic link email
- `useVerifyMagicLink()` - Verify magic link token
- `useGmailAuthUrl()` - Get Gmail OAuth URL (manual trigger)
- `useGmailConnect()` - Connect Gmail account
- `useGmailDisconnect()` - Disconnect Gmail account
- `useAuth()` - Combined hook with all auth state

#### `/frontend/src/hooks/useQueue.ts`
Queue management with optimistic updates:

- `useQueue(params)` - Fetch queue items (30s auto-refetch)
- `useApprove()` - Approve action (optimistic remove)
- `useOverride()` - Override action (optimistic remove)
- `useEdit()` - Edit action content (optimistic update)
- `useEscalate()` - Escalate action
- `useQueueActions()` - Combined hook for all actions

**Optimistic Updates:**
- Items removed immediately from UI on approve/override
- Changes reverted if mutation fails
- Automatic cache invalidation after mutations

#### `/frontend/src/hooks/useStats.ts`
Statistics with auto-refresh:

- `useStats()` - Fetch all stats (15s auto-refetch)
- `useNavigationCounts()` - Navigation counts only
- `useEfficiencyStats()` - Efficiency stats only
- `useGlobalStatus()` - Global status only

#### `/frontend/src/hooks/useConversations.ts`
Conversation fetching:

- `useConversation(id)` - Fetch by conversation ID
- `useConversationByObjective(objectiveId)` - Fetch by objective ID

### Updated Store

#### `/frontend/src/stores/appStore.ts`
Simplified Zustand store:

**State:**
- `user` - Current user (synced with React Query)
- `isAuthenticated` - Auth status
- `activeView` - Current view filter
- `selectedCardId` - Selected card ID
- `selectedObjectiveId` - Selected objective ID
- `activeFilter` - Queue filter (all/high_risk/low_confidence)

**Persistence:**
- Only UI preferences persisted (activeView, activeFilter)
- Auth state managed by React Query and API tokens

### Updated App Component

#### `/frontend/src/App.tsx`
- Wrapped with `QueryClientProvider`
- Uses React Query hooks for data fetching
- Loading states with spinner
- Proper error handling
- Separated into `App` (provider) and `AppContent` (logic)

## Usage Examples

### Authentication

```typescript
import { useAuth, useLogin } from './hooks';

function LoginForm() {
  const { login, isLoginLoading, loginError } = useAuth();

  const handleLogin = () => {
    login(
      { email: 'user@example.com', password: 'password' },
      {
        onSuccess: () => {
          // User automatically cached and available via useAuth
        },
        onError: (error) => {
          console.error('Login failed:', error);
        }
      }
    );
  };

  return (
    <button onClick={handleLogin} disabled={isLoginLoading}>
      {isLoginLoading ? 'Logging in...' : 'Login'}
    </button>
  );
}
```

### Queue Management

```typescript
import { useQueue, useQueueActions } from './hooks';

function QueueList() {
  const { data: items, isLoading } = useQueue({ filter: 'all' });
  const { approve, isApproving } = useQueueActions();

  const handleApprove = (id: string) => {
    approve(
      { id },
      {
        onSuccess: () => {
          // Item automatically removed from cache
          console.log('Approved successfully');
        }
      }
    );
  };

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      {items?.map(item => (
        <div key={item.id}>
          <p>{item.summary}</p>
          <button
            onClick={() => handleApprove(item.id)}
            disabled={isApproving}
          >
            Approve
          </button>
        </div>
      ))}
    </div>
  );
}
```

### Statistics Dashboard

```typescript
import { useStats } from './hooks';

function Dashboard() {
  const { data: stats, isLoading } = useStats();

  if (isLoading) return <div>Loading stats...</div>;

  return (
    <div>
      <p>Pending: {stats?.globalStatus.pendingCount}</p>
      <p>Handled: {stats?.navigationCounts.handledByAI}</p>
      <p>Efficiency: {stats?.efficiencyStats.percentage}%</p>
    </div>
  );
}
```

### Conversation View

```typescript
import { useConversationByObjective } from './hooks';
import { useAppStore } from './stores/appStore';

function ConversationPanel() {
  const selectedObjectiveId = useAppStore(s => s.selectedObjectiveId);
  const { data: conversation, isLoading } = useConversationByObjective(selectedObjectiveId);

  if (!selectedObjectiveId) return <div>Select a card</div>;
  if (isLoading) return <div>Loading conversation...</div>;

  return (
    <div>
      <h2>{conversation?.objectiveTitle}</h2>
      {conversation?.timeline.map(item => (
        <div key={item.id}>
          <p>{item.sender}: {item.content}</p>
        </div>
      ))}
    </div>
  );
}
```

## API Endpoints

### Authentication
- `POST /api/auth/login` - Email/password login
- `POST /api/auth/register` - User registration
- `GET /api/auth/me` - Get current user
- `POST /api/auth/magic-link/request` - Request magic link
- `POST /api/auth/magic-link/verify` - Verify magic link
- `GET /api/auth/gmail/authorize` - Get Gmail OAuth URL
- `POST /api/auth/gmail/callback` - Handle Gmail OAuth callback
- `POST /api/auth/gmail/disconnect` - Disconnect Gmail

### Queue
- `GET /api/queue` - Get queue items (with filters)
- `POST /api/queue/:id/approve` - Approve action
- `POST /api/queue/:id/override` - Override action
- `PATCH /api/queue/:id` - Edit action content
- `POST /api/queue/:id/escalate` - Escalate action

### Statistics
- `GET /api/stats` - Get all statistics

### Conversations
- `GET /api/conversations/:id` - Get conversation by ID
- `GET /api/objectives/:id/conversation` - Get conversation by objective

## Configuration

### Environment Variables

Create `.env` file (see `.env.example`):

```bash
# Backend API URL
VITE_API_BASE_URL=http://localhost:8000
```

### Query Client Defaults

Configured in `/frontend/src/lib/queryClient.ts`:

```typescript
{
  staleTime: 30 * 1000,        // 30 seconds
  gcTime: 5 * 60 * 1000,       // 5 minutes
  refetchOnWindowFocus: true,
  refetchOnMount: false,
  retry: 2,
}
```

## Error Handling

### API Errors

All API errors are transformed to `ApiError` class:

```typescript
try {
  await api.queue.approve(id);
} catch (error) {
  if (error instanceof ApiError) {
    console.log(error.status);      // HTTP status code
    console.log(error.statusText);  // Status text
    console.log(error.data);        // Error response data
  }
}
```

### 401 Unauthorized

- Automatically removes auth token
- Redirects to `/login`
- Clears all query cache

### Network Errors

- Automatic retry with exponential backoff
- Status code 0 indicates network failure

## Cache Invalidation

Mutations automatically invalidate related queries:

- **Approve/Override/Escalate**: Invalidates queue and stats
- **Edit**: Invalidates specific item and queue list
- **Login/Register**: Invalidates user query
- **Logout**: Clears entire cache

## Optimistic Updates

Queue actions use optimistic updates for instant UI feedback:

1. **On mutation**: Remove/update item immediately
2. **On error**: Rollback to previous state
3. **On settle**: Refetch to ensure consistency

## TypeScript Support

All API calls are fully type-safe:

```typescript
const { data } = useQueue();
// data is typed as ActionCard[]

const { approve } = useQueueActions();
// approve requires { id: string }

const { data: user } = useCurrentUser();
// user is typed as User
```

## Best Practices

1. **Always use hooks** - Don't call `api.*` directly in components
2. **Handle loading states** - Check `isLoading` from queries
3. **Handle errors** - Check `error` from queries/mutations
4. **Use optimistic updates** - For better UX on mutations
5. **Invalidate cache** - After mutations that change server state
6. **Use query keys factory** - From `queryKeys` in queryClient.ts

## Testing

Example test structure:

```typescript
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useQueue } from './hooks/useQueue';

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } }
  });

  return ({ children }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

test('useQueue fetches data', async () => {
  const { result } = renderHook(() => useQueue(), {
    wrapper: createWrapper(),
  });

  await waitFor(() => expect(result.current.isSuccess).toBe(true));
  expect(result.current.data).toBeDefined();
});
```

## Migration from Mock Data

To migrate from mock data to real API:

1. Set `VITE_API_BASE_URL` in `.env`
2. Ensure backend is running
3. Remove mock data imports from components
4. Components already use React Query hooks
5. Test with real backend endpoints

## Troubleshooting

### CORS Errors
Ensure backend has CORS enabled for frontend origin.

### 401 Errors
- Check token in localStorage (`getanswers_auth_token`)
- Verify backend authentication endpoint

### Stale Data
- Adjust `staleTime` in query options
- Manually invalidate with `queryClient.invalidateQueries()`

### Network Errors
- Check `VITE_API_BASE_URL` configuration
- Verify backend is running
- Check browser network tab

## Future Enhancements

Potential improvements:

1. **React Query Devtools** - Add `@tanstack/react-query-devtools`
2. **Websocket Support** - Real-time updates instead of polling
3. **Offline Support** - Persist mutations when offline
4. **Request Deduplication** - Automatic with React Query
5. **Pagination** - Add infinite queries for large lists
6. **Search/Filter** - Server-side search with debouncing
