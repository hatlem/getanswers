// Central export file for all React Query hooks
// Makes importing hooks easier across the application

export {
  useCurrentUser,
  useLogin,
  useRegister,
  useLogout,
  useRequestMagicLink,
  useVerifyMagicLink,
  useGmailAuthUrl,
  useGmailConnect,
  useGmailDisconnect,
  useAuth,
} from './useAuth';

export {
  useQueue,
  useApprove,
  useOverride,
  useEdit,
  useEscalate,
  useQueueActions,
} from './useQueue';

export {
  useStats,
  useNavigationCounts,
  useEfficiencyStats,
  useGlobalStatus,
} from './useStats';

export {
  useConversation,
  useConversationByObjective,
} from './useConversations';
