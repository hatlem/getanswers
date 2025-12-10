import type { ActionCard, ConversationThread, NavigationCount, EfficiencyStats, GlobalStatus, User } from '../types';

export const mockUser: User = {
  id: 'user-1',
  email: 'jane.doe@company.com',
  name: 'Jane Doe',
  autonomyLevel: 'high',
  createdAt: '2024-01-15T10:00:00Z',
};

export const mockGlobalStatus: GlobalStatus = {
  status: 'pending_decisions',
  message: '3 Decisions Pending',
  pendingCount: 3,
};

export const mockNavigationCounts: NavigationCount = {
  needsDecision: 3,
  waitingOnOthers: 8,
  handledByAI: 104,
  scheduledDone: 5,
  muted: 22,
};

export const mockEfficiencyStats: EfficiencyStats = {
  handledAutonomously: 104,
  totalToday: 111,
  percentage: 94,
};

export const mockActionCards: ActionCard[] = [
  {
    id: 'card-1',
    objectiveId: 'obj-1',
    priorityScore: 95,
    riskLevel: 'high',
    category: 'finance',
    confidenceScore: 62,
    summary: 'Supplier requests a 10-day extension on the Q4 payment deadline.',
    proposedAction: 'I suggest we accept to maintain good relations, but add a 2% late fee clause to the new draft agreement.',
    sender: {
      id: 'sender-1',
      name: 'Jane Doe',
      email: 'jane@acmecorp.com',
      organization: 'Acme Corp.',
      avatarColor: 'linear-gradient(135deg, #ef4444, #f97316)',
      tags: [{ label: 'VIP Supplier', type: 'vip' }],
    },
    relatedItems: [
      { id: 'rel-1', label: 'Invoice #485-B', href: '#', type: 'invoice' },
      { id: 'rel-2', label: 'Contract #AC-2024', href: '#', type: 'contract' },
    ],
    createdAt: '2024-12-10T09:42:00Z',
    updatedAt: '2024-12-10T14:18:00Z',
  },
  {
    id: 'card-2',
    objectiveId: 'obj-2',
    priorityScore: 78,
    riskLevel: 'medium',
    category: 'client',
    confidenceScore: 78,
    summary: 'Client requests scope change for Project Phoenix deliverables.',
    proposedAction: 'Schedule a 30-minute call to discuss implications. Draft email proposes Thursday 2pm or Friday 10am slots.',
    sender: {
      id: 'sender-2',
      name: 'Michael Santos',
      email: 'michael@techventures.com',
      organization: 'TechVentures Inc.',
      avatarColor: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
      tags: [{ label: 'Key Account', type: 'key' }],
    },
    relatedItems: [
      { id: 'rel-3', label: 'Project Phoenix', href: '#', type: 'project' },
      { id: 'rel-4', label: 'SOW v2.1', href: '#', type: 'document' },
    ],
    createdAt: '2024-12-10T11:15:00Z',
    updatedAt: '2024-12-10T13:45:00Z',
  },
  {
    id: 'card-3',
    objectiveId: 'obj-3',
    priorityScore: 45,
    riskLevel: 'low',
    category: 'hr',
    confidenceScore: 45,
    isUncertain: true,
    summary: 'New hire onboarding: Equipment preferences and start date confirmation.',
    proposedAction: "I'm uncertain about laptop configuration preferences. Draft asks for clarification on developer vs. standard setup.",
    sender: {
      id: 'sender-3',
      name: 'Alex Rivera',
      email: 'alex.rivera@newmail.com',
      organization: 'New Hire - Engineering',
      avatarColor: 'linear-gradient(135deg, #10b981, #34d399)',
      tags: [{ label: 'Starting Jan 15', type: 'new' }],
    },
    relatedItems: [
      { id: 'rel-5', label: 'Offer Letter', href: '#', type: 'document' },
      { id: 'rel-6', label: 'IT Request #892', href: '#', type: 'ticket' },
    ],
    createdAt: '2024-12-10T08:30:00Z',
    updatedAt: '2024-12-10T12:00:00Z',
  },
];

export const mockConversation: ConversationThread = {
  id: 'conv-1',
  objectiveId: 'obj-1',
  objectiveTitle: 'Negotiate Q4 payment terms',
  objectiveStatus: 'waiting_on_you',
  agentSummary: 'They originally requested a 14-day extension; I negotiated down to 10 days. The current draft includes the 2% late fee clause as a safeguard. Their latest reply accepts the timeline but asks for confirmation on the fee structure. Awaiting your approval to finalize.',
  timeline: [
    {
      id: 'tl-1',
      type: 'incoming',
      sender: 'Jane Doe',
      timestamp: '2024-12-10T09:42:00Z',
      content: "Hi Team, Given our current cash flow situation, we'd like to request a 14-day extension on the Q4 payment deadline...",
      fullContent: "Hi Team,\n\nGiven our current cash flow situation, we'd like to request a 14-day extension on the Q4 payment deadline. We've had some unexpected delays with our own receivables, and this would help us maintain a healthy cash position.\n\nWe value our partnership and hope you can accommodate this request. Please let us know if you need any additional information.\n\nBest regards,\nJane Doe\nAccounts Payable, Acme Corp.",
      isCollapsed: true,
    },
    {
      id: 'tl-2',
      type: 'agent_action',
      sender: 'GetAnswers Agent',
      timestamp: '2024-12-10T09:43:00Z',
      content: 'Proposed counter-offer: 10-day extension with 2% late fee clause. Tone: Professional, accommodating.',
      badge: 'auto',
    },
    {
      id: 'tl-3',
      type: 'outgoing',
      sender: 'You (via Agent)',
      timestamp: '2024-12-10T10:15:00Z',
      content: 'Counter-proposal sent with 10-day extension and fee clause. Email included relationship acknowledgment.',
      badge: 'sent',
    },
    {
      id: 'tl-4',
      type: 'incoming',
      sender: 'Jane Doe',
      timestamp: '2024-12-10T14:18:00Z',
      content: 'Thank you for the flexibility. We can work with 10 days. Just need clarification on how the fee would be calculated...',
      fullContent: "Thank you for the flexibility. We can work with 10 days. Just need clarification on how the fee would be calculated if we do need to use the extension.\n\nWould it be:\na) 2% flat fee on the total outstanding balance?\nb) 2% per week delayed?\nc) Something else?\n\nLet me know and we can finalize the agreement.\n\nThanks,\nJane",
      badge: 'new',
      isCollapsed: true,
    },
    {
      id: 'tl-5',
      type: 'agent_action',
      sender: 'GetAnswers Agent',
      timestamp: '2024-12-10T14:20:00Z',
      content: 'Draft ready: Confirms fee calculation method (2% of outstanding balance per week delayed). Includes amended contract attachment.',
      badge: 'pending',
    },
  ],
  createdAt: '2024-12-10T09:42:00Z',
  updatedAt: '2024-12-10T14:20:00Z',
};
