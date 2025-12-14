// Core domain types for GetAnswers Mission Control

export type RiskLevel = 'high' | 'medium' | 'low';
export type ObjectiveStatus = 'waiting_on_you' | 'waiting_on_others' | 'handled' | 'scheduled' | 'muted';
export type TimelineItemType = 'incoming' | 'outgoing' | 'agent_action';
export type TimelineBadge = 'auto' | 'sent' | 'pending' | 'new';
export type CategoryType = 'finance' | 'client' | 'hr' | 'legal' | 'internal' | 'partner';

export interface Sender {
  id: string;
  name: string;
  email: string;
  organization?: string;
  avatarUrl?: string;
  avatarColor?: string;
  tags: SenderTag[];
}

export interface SenderTag {
  label: string;
  type: 'vip' | 'key' | 'new' | 'blocked' | 'custom';
}

export interface RelatedItem {
  id: string;
  label: string;
  href: string;
  type: 'invoice' | 'contract' | 'project' | 'document' | 'ticket';
}

export interface ActionCard {
  id: string;
  objectiveId: string;
  priorityScore: number;
  riskLevel: RiskLevel;
  category: CategoryType;
  confidenceScore: number;
  summary: string;
  proposedAction: string;
  isUncertain?: boolean;
  sender: Sender;
  relatedItems: RelatedItem[];
  createdAt: string;
  updatedAt: string;
}

export interface TimelineItem {
  id: string;
  type: TimelineItemType;
  sender: string;
  senderAvatar?: string;
  timestamp: string;
  content: string;
  fullContent?: string;
  badge?: TimelineBadge;
  isCollapsed?: boolean;
}

export interface ConversationThread {
  id: string;
  objectiveId: string;
  objectiveTitle: string;
  objectiveStatus: ObjectiveStatus;
  agentSummary: string;
  timeline: TimelineItem[];
  createdAt: string;
  updatedAt: string;
}

export interface Objective {
  id: string;
  title: string;
  status: ObjectiveStatus;
  description?: string;
  conversationIds: string[];
  createdAt: string;
  updatedAt: string;
}

export interface NavigationCount {
  needsDecision: number;
  waitingOnOthers: number;
  handledByAI: number;
  scheduledDone: number;
  muted: number;
}

export interface EfficiencyStats {
  handledAutonomously: number;
  totalToday: number;
  percentage: number;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  is_personal: boolean;
}

export interface User {
  id: string;
  email: string;
  name: string;
  avatarUrl?: string;
  autonomyLevel?: 'low' | 'medium' | 'high';
  onboarding_completed: boolean;
  needs_password_setup: boolean;
  is_super_admin?: boolean;
  current_organization?: Organization | null;
  createdAt?: string;
  created_at?: string;
}

export interface GlobalStatus {
  status: 'all_clear' | 'pending_decisions' | 'urgent';
  message: string;
  pendingCount: number;
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  success: boolean;
  error?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

// Action types for mutations
export type ActionType = 'approve' | 'edit' | 'override' | 'escalate';

export interface ActionPayload {
  cardId: string;
  action: ActionType;
  editedContent?: string;
  reason?: string;
}

// Additional Auth types
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials {
  email: string;
  password: string;
  name: string;
}

export interface MagicLinkRequest {
  email: string;
}

export interface MagicLinkVerification {
  token: string;
}

export interface GmailCallbackParams {
  code: string;
  state: string;
}

// Queue Response type (from backend)
export interface QueueResponse {
  cards: ActionCard[];
  total: number;
  needs_decision: number;
  waiting_on_others: number;
  handled_by_ai: number;
  scheduled_done: number;
  muted: number;
}
