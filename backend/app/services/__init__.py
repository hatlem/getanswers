# GetAnswers Services

from .agent import (
    AgentService,
    EmailAnalysis,
    DraftResponse,
    PolicyMatch,
    RiskAssessment,
    EmailIntent,
    ExtractedEntity,
)
from .gmail import (
    GmailService,
    GmailServiceError,
    GmailAuthError,
    GmailAPIError,
    GmailRateLimitError,
)
from .outlook import (
    OutlookService,
    OutlookServiceError,
    OutlookAuthError,
    OutlookAPIError,
    get_outlook_service,
)
from .email import (
    EmailService,
    email_service,
)
from .dependencies import (
    get_agent_service,
    get_agent_service_fresh,
    reset_agent_service,
    get_gmail_service,
)
from .triage import (
    TriageService,
    SyncResult,
    ExecutionResult,
    ProcessingResult,
    ObjectiveGroupingResult,
)
from .stripe import (
    get_stripe_mode,
    invalidate_stripe_mode_cache,
    get_stripe_client,
    get_publishable_key,
    StripeService,
)
from .features import FeatureService

__all__ = [
    # Agent service and models
    "AgentService",
    "EmailAnalysis",
    "DraftResponse",
    "PolicyMatch",
    "RiskAssessment",
    "EmailIntent",
    "ExtractedEntity",
    # Gmail service and exceptions
    "GmailService",
    "GmailServiceError",
    "GmailAuthError",
    "GmailAPIError",
    "GmailRateLimitError",
    # Outlook service and exceptions
    "OutlookService",
    "OutlookServiceError",
    "OutlookAuthError",
    "OutlookAPIError",
    "get_outlook_service",
    # Email service (transactional emails via GetMailer)
    "EmailService",
    "email_service",
    # Dependencies
    "get_agent_service",
    "get_agent_service_fresh",
    "reset_agent_service",
    "get_gmail_service",
    # Triage service and models
    "TriageService",
    "SyncResult",
    "ExecutionResult",
    "ProcessingResult",
    "ObjectiveGroupingResult",
    # Stripe service
    "get_stripe_mode",
    "invalidate_stripe_mode_cache",
    "get_stripe_client",
    "get_publishable_key",
    "StripeService",
    # Feature service
    "FeatureService",
]
