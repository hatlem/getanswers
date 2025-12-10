# Frontend API Integration - Complete Guide

This document outlines the completed frontend API integration work and remaining steps to get the GetAnswers application fully functional.

## Completed Work

### 1. UI Components Created

#### Loading States (`/frontend/src/components/ui/Skeleton.tsx`)
- `ActionCardSkeleton` - Loading skeleton for action cards in queue
- `TimelineSkeleton` - Loading skeleton for conversation timeline
- `StatsSkeleton` - Loading skeleton for efficiency stats
- `NavItemSkeleton` - Loading skeleton for navigation items
- `ConversationHeaderSkeleton` - Loading skeleton for conversation header
- `AgentSummarySkeleton` - Loading skeleton for agent summary

#### Error States (`/frontend/src/components/ui/ErrorState.tsx`)
- `ErrorState` - Full-page error display with retry button
- `InlineError` - Compact error display for smaller spaces
- Automatic detection of network vs server errors
- Development mode shows technical details

#### Empty States (`/frontend/src/components/ui/EmptyState.tsx`)
- `EmptyQueueState` - Shown when queue is empty
- `NoConversationState` - Shown when no conversation is selected
- `NoSearchResultsState` - Shown when search returns no results
- `NoFilterResultsState` - Shown when filter returns no items

#### Toast Notifications (`/frontend/src/lib/toast.tsx`)
- Configured react-hot-toast with app theme
- Success, error, warning, info toast variants
- Pre-configured action toasts (approve, override, edit, escalate)
- Promise-based toasts for async operations

### 2. Integration Updates

#### main.tsx
- Added QueryClientProvider wrapper
- Added Toaster component for notifications
- Added ReactQueryDevtools for development

#### App.tsx (Dashboard component)
- Integrated useAuth hook for user data
- Integrated useStats hook for navigation counts and efficiency stats
- Integrated useQueueActions for action mutations
- Added toast notifications for all queue actions
- Removed mock data dependencies
- Loading state shown during initial data fetch

#### LeftColumn.tsx
- Made counts and stats optional (shows skeleton when loading)
- Added StatsSkeleton for loading efficiency stats
- Gracefully handles missing data

#### CenterColumn.tsx
- Integrated useQueue hook to fetch queue data
- Added loading skeletons (shows 3 cards while loading)
- Added error state with retry button
- Added empty state variants (no items vs no filter results)
- Filters now work with real API data
- Removed dependency on passed props (self-contained)

#### RightColumn.tsx
- Changed from receiving conversation prop to receiving objectiveId
- Integrated useConversationByObjective hook
- Added loading skeletons for header, summary, and timeline
- Added error state with retry button
- Shows empty state when no conversation selected

### 3. Configuration Files

#### `/frontend/src/lib/queryClient.ts`
Already configured with:
- Stale time: 30 seconds
- Cache time: 5 minutes
- Automatic refetch on window focus
- Query key factory for consistency

#### `/frontend/src/lib/api.ts`
Already configured with:
- Token management
- Request/response interceptors
- Automatic 401 handling
- Type-safe endpoints

#### `/frontend/src/hooks/`
Already created:
- `useAuth.ts` - Authentication operations
- `useQueue.ts` - Queue fetching and mutations with optimistic updates
- `useStats.ts` - Statistics fetching
- `useConversations.ts` - Conversation fetching

## Required Installation

Before running the application, install the required package:

```bash
cd frontend
npm install react-hot-toast
```

## How It Works

### Data Flow

1. **App Initialization**
   - main.tsx provides QueryClientProvider to entire app
   - Dashboard component loads initial stats (shows loading spinner)
   - Once stats loaded, shows full UI

2. **Navigation**
   - LeftColumn displays navigation counts from stats
   - Shows loading skeleton while stats fetch
   - Updates every 15 seconds automatically

3. **Queue Display**
   - CenterColumn fetches its own queue data based on activeView and activeFilter
   - Shows loading skeletons while fetching
   - Updates every 30 seconds automatically
   - Displays appropriate empty state if no items

4. **Conversation Display**
   - RightColumn fetches conversation when objectiveId changes
   - Shows loading skeletons while fetching
   - Displays empty state when nothing selected
   - Refetches on window focus

5. **Actions**
   - User clicks approve/override/edit/escalate on a card
   - Optimistic update immediately removes card from queue
   - API call executes in background
   - Success: Shows toast, updates stats, card stays removed
   - Error: Rollback (card reappears), shows error toast

### Optimistic Updates

All queue mutations use optimistic updates:
- **Approve**: Card immediately removed from queue
- **Override**: Card immediately removed from queue
- **Edit**: Card updates immediately with new content
- **Escalate**: Card updates immediately with escalation status

If the API call fails, changes are automatically rolled back and an error toast appears.

### Real-time Updates

- **Queue**: Refetches every 30 seconds
- **Stats**: Refetches every 15 seconds
- **Conversations**: Refetches on window focus
- All data is cached and reused when fresh

## Missing Pieces

### 1. Backend API Endpoints

The frontend expects these endpoints to be implemented:

#### Authentication
- `POST /api/auth/login` - Email/password login
- `POST /api/auth/register` - User registration
- `GET /api/auth/me` - Get current user
- `POST /api/auth/magic-link/request` - Request magic link
- `POST /api/auth/magic-link/verify` - Verify magic link
- `GET /api/auth/gmail/authorize` - Get Gmail OAuth URL
- `POST /api/auth/gmail/callback` - Handle Gmail OAuth callback
- `POST /api/auth/gmail/disconnect` - Disconnect Gmail

#### Queue Management
- `GET /api/queue?filter=all&status=needs_decision` - Get queue items
- `POST /api/queue/:id/approve` - Approve an action
- `POST /api/queue/:id/override` - Override an action
- `PATCH /api/queue/:id` - Edit action content
- `POST /api/queue/:id/escalate` - Escalate an action

#### Statistics
- `GET /api/stats` - Get navigation counts, efficiency stats, and global status

#### Conversations
- `GET /api/conversations/:id` - Get conversation by ID
- `GET /api/objectives/:objectiveId/conversation` - Get conversation by objective ID

### 2. Authentication Components

These components are referenced but need to be created:
- `/frontend/src/components/auth/LoginPage.tsx`
- `/frontend/src/components/auth/RegisterPage.tsx`
- `/frontend/src/components/auth/MagicLinkPage.tsx`
- `/frontend/src/components/auth/GmailCallbackPage.tsx`
- `/frontend/src/components/auth/ProtectedRoute.tsx`

### 3. Environment Variables

Create `/frontend/.env` with:
```env
VITE_API_BASE_URL=http://localhost:8000
```

For production:
```env
VITE_API_BASE_URL=https://api.getanswers.com
```

## Testing the Integration

### 1. With Mock Backend

Create a mock server that returns the expected data structures:

```typescript
// Example queue response
GET /api/queue
{
  "items": [
    {
      "id": "card-1",
      "objectiveId": "obj-1",
      "priorityScore": 95,
      "riskLevel": "high",
      "category": "finance",
      "confidenceScore": 62,
      "summary": "...",
      "proposedAction": "...",
      "sender": { ... },
      "relatedItems": [ ... ],
      "createdAt": "2024-12-10T09:42:00Z",
      "updatedAt": "2024-12-10T14:18:00Z"
    }
  ]
}

// Example stats response
GET /api/stats
{
  "navigationCounts": {
    "needsDecision": 3,
    "waitingOnOthers": 8,
    "handledByAI": 104,
    "scheduledDone": 5,
    "muted": 22
  },
  "efficiencyStats": {
    "handledAutonomously": 104,
    "totalToday": 111,
    "percentage": 94
  },
  "globalStatus": {
    "status": "pending_decisions",
    "message": "3 Decisions Pending",
    "pendingCount": 3
  }
}
```

### 2. Development Mode

The app includes React Query DevTools for debugging:
- Click the React Query icon in bottom corner
- View all queries and their states
- Manually trigger refetches
- Inspect cache data

### 3. Error Testing

Test error handling by:
1. Stopping the backend (network errors)
2. Returning 500 errors from backend
3. Returning 401 errors (automatic redirect to login)
4. Returning empty arrays (empty states)

## Performance Features

### Caching Strategy
- **Fresh Data**: 10-30 seconds depending on data type
- **Cache Duration**: 5 minutes before garbage collection
- **Background Updates**: Data refetches while showing cached version

### Network Optimization
- **Deduplication**: Multiple requests for same data are combined
- **Parallel Requests**: Independent queries run in parallel
- **Retry Logic**: Failed requests retry with exponential backoff

### User Experience
- **Optimistic Updates**: Actions feel instant
- **Skeleton Loading**: Better perceived performance
- **Smooth Transitions**: Framer Motion animations throughout
- **Error Recovery**: Clear retry buttons and messages

## Future Enhancements

### WebSocket Integration
Replace polling with WebSocket for real-time updates:

```typescript
// In queryClient.ts
import { io } from 'socket.io-client';

const socket = io(import.meta.env.VITE_WS_URL);

socket.on('queue:updated', () => {
  queryClient.invalidateQueries({ queryKey: queryKeys.queue.all });
});

socket.on('stats:updated', () => {
  queryClient.invalidateQueries({ queryKey: queryKeys.stats.all });
});
```

### Pagination
For large queues, implement cursor-based pagination:

```typescript
const { data, fetchNextPage, hasNextPage } = useInfiniteQuery({
  queryKey: queryKeys.queue.list(params),
  queryFn: ({ pageParam = 0 }) =>
    api.queue.getQueue({ ...params, offset: pageParam }),
  getNextPageParam: (lastPage, pages) =>
    lastPage.length === 0 ? undefined : pages.length * 20,
});
```

### Offline Support
Add service worker for offline functionality:

```typescript
// In queryClient.ts
const persistedQueryClient = createSyncStoragePersister({
  storage: window.localStorage,
});

// Wrap app with PersistQueryClientProvider
```

## Troubleshooting

### Issue: Queries not fetching
- Check browser network tab for API calls
- Verify VITE_API_BASE_URL is correct
- Check React Query DevTools for query state

### Issue: Optimistic updates not working
- Check mutation configuration in hooks
- Verify query keys match between hooks
- Check browser console for errors

### Issue: Toast not appearing
- Verify react-hot-toast is installed
- Check Toaster component is mounted in main.tsx
- Verify toast functions are called with correct params

### Issue: Loading states stuck
- Check if API is returning responses
- Verify response format matches TypeScript types
- Check for JavaScript errors in console

## Summary

The frontend is now fully integrated with the API architecture and ready for backend connection. All mock data has been replaced with real API calls, proper loading/error states are in place, and the user experience is professional and responsive. Once the backend endpoints are implemented and the authentication components are created, the application will be fully functional.
