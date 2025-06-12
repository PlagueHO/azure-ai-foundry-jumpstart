using Microsoft.Extensions.Logging;
using TechSupportChatAgent.Models;

namespace TechSupportChatAgent.Services;

/// <summary>
/// Service for managing conversation sessions and message history.
/// </summary>
public class ConversationManager
{
    private readonly ILogger<ConversationManager> _logger;
    private readonly Dictionary<string, ConversationSession> _activeSessions = new();
    private readonly Dictionary<string, List<ChatMessage>> _conversationHistory = new();

    public ConversationManager(ILogger<ConversationManager> logger)
    {
        _logger = logger;
    }

    /// <summary>
    /// Creates a new conversation session.
    /// </summary>
    /// <returns>A new conversation session.</returns>
    public ConversationSession CreateNewSession()
    {
        var session = new ConversationSession();
        _activeSessions[session.SessionId] = session;
        _conversationHistory[session.SessionId] = new List<ChatMessage>();
        
        _logger.LogInformation("Created new conversation session: {SessionId}", session.SessionId);
        
        return session;
    }

    /// <summary>
    /// Gets an existing conversation session.
    /// </summary>
    /// <param name="sessionId">The session ID.</param>
    /// <returns>The conversation session if found, null otherwise.</returns>
    public ConversationSession? GetSession(string sessionId)
    {
        return _activeSessions.TryGetValue(sessionId, out var session) ? session : null;
    }

    /// <summary>
    /// Adds a message to the conversation history.
    /// </summary>
    /// <param name="session">The conversation session.</param>
    /// <param name="message">The message to add.</param>
    public void AddMessage(ConversationSession session, ChatMessage message)
    {
        if (!_conversationHistory.TryGetValue(session.SessionId, out var messages))
        {
            messages = new List<ChatMessage>();
            _conversationHistory[session.SessionId] = messages;
        }

        messages.Add(message);
        
        _logger.LogDebug("Added {Role} message to session {SessionId}: {Content}", 
            message.Role, session.SessionId, message.Content);
    }

    /// <summary>
    /// Gets the conversation history for a session.
    /// </summary>
    /// <param name="sessionId">The session ID.</param>
    /// <returns>List of messages in the conversation.</returns>
    public List<ChatMessage> GetConversationHistory(string sessionId)
    {
        return _conversationHistory.TryGetValue(sessionId, out var messages) 
            ? new List<ChatMessage>(messages) 
            : new List<ChatMessage>();
    }

    /// <summary>
    /// Gets recent messages from the conversation (for context).
    /// </summary>
    /// <param name="sessionId">The session ID.</param>
    /// <param name="messageCount">Number of recent messages to retrieve.</param>
    /// <returns>List of recent messages.</returns>
    public List<ChatMessage> GetRecentMessages(string sessionId, int messageCount = 10)
    {
        if (!_conversationHistory.TryGetValue(sessionId, out var messages))
            return new List<ChatMessage>();

        return messages.TakeLast(messageCount).ToList();
    }

    /// <summary>
    /// Updates the session with attempted troubleshooting steps.
    /// </summary>
    /// <param name="session">The conversation session.</param>
    /// <param name="step">The troubleshooting step that was attempted.</param>
    public void AddAttemptedStep(ConversationSession session, string step)
    {
        if (!session.PreviousSteps.Contains(step))
        {
            session.PreviousSteps.Add(step);
            _logger.LogDebug("Added attempted step to session {SessionId}: {Step}", 
                session.SessionId, step);
        }
    }

    /// <summary>
    /// Marks a session as requiring escalation.
    /// </summary>
    /// <param name="session">The conversation session.</param>
    /// <param name="reason">The reason for escalation.</param>
    public void MarkForEscalation(ConversationSession session, string reason)
    {
        session.RequiresEscalation = true;
        session.EscalationCount++;
        session.Metadata["escalation_reason"] = reason;
        session.Metadata["escalation_timestamp"] = DateTime.UtcNow;
        
        _logger.LogInformation("Session {SessionId} marked for escalation: {Reason}", 
            session.SessionId, reason);
    }

    /// <summary>
    /// Ends a conversation session and cleans up resources.
    /// </summary>
    /// <param name="sessionId">The session ID to end.</param>
    public void EndSession(string sessionId)
    {
        if (_activeSessions.TryGetValue(sessionId, out var session))
        {
            _logger.LogInformation("Ending conversation session: {SessionId}, Duration: {Duration}", 
                sessionId, DateTime.UtcNow - session.StartTime);
        }

        _activeSessions.Remove(sessionId);
        
        // Keep conversation history for a short time for potential escalation handoff
        // In a production system, this might be persisted to a database
        Task.Run(async () =>
        {
            await Task.Delay(TimeSpan.FromMinutes(30)); // Keep history for 30 minutes
            _conversationHistory.Remove(sessionId);
        });
    }

    /// <summary>
    /// Gets session analytics for monitoring and improvement.
    /// </summary>
    /// <param name="sessionId">The session ID.</param>
    /// <returns>Analytics data for the session.</returns>
    public SessionAnalytics GetSessionAnalytics(string sessionId)
    {
        var session = GetSession(sessionId);
        var messages = GetConversationHistory(sessionId);
        
        if (session == null)
        {
            return new SessionAnalytics { SessionId = sessionId };
        }

        var userMessages = messages.Where(m => m.Role == ChatRole.User).ToList();
        var assistantMessages = messages.Where(m => m.Role == ChatRole.Assistant).ToList();

        return new SessionAnalytics
        {
            SessionId = sessionId,
            StartTime = session.StartTime,
            Duration = DateTime.UtcNow - session.StartTime,
            TotalMessages = messages.Count,
            UserMessages = userMessages.Count,
            AssistantMessages = assistantMessages.Count,
            EscalationCount = session.EscalationCount,
            RequiresEscalation = session.RequiresEscalation,
            AttemptedStepsCount = session.PreviousSteps.Count,
            CurrentIssue = session.CurrentIssue
        };
    }

    /// <summary>
    /// Gets all active sessions (for administrative purposes).
    /// </summary>
    /// <returns>List of active session IDs.</returns>
    public List<string> GetActiveSessionIds()
    {
        return _activeSessions.Keys.ToList();
    }

    /// <summary>
    /// Creates a summary of the conversation for escalation handoff.
    /// </summary>
    /// <param name="sessionId">The session ID.</param>
    /// <returns>A summary of the conversation for human agents.</returns>
    public ConversationSummary CreateEscalationSummary(string sessionId)
    {
        var session = GetSession(sessionId);
        var messages = GetConversationHistory(sessionId);
        var analytics = GetSessionAnalytics(sessionId);

        if (session == null)
        {
            throw new ArgumentException($"Session {sessionId} not found", nameof(sessionId));
        }

        var userMessages = messages.Where(m => m.Role == ChatRole.User).ToList();
          return new ConversationSummary
        {
            SessionId = sessionId,
            StartTime = session.StartTime,
            Duration = analytics.Duration,
            CustomerIssue = session.CurrentIssue,
            MessageCount = messages.Count,
            AttemptedSteps = session.PreviousSteps.ToList(),
            EscalationReason = session.Metadata.TryGetValue("escalation_reason", out var reason) 
                ? reason?.ToString() ?? "Customer request" : "Customer request",
            KeyUserMessages = userMessages.TakeLast(5).Select(m => m.Content).ToList(),
            SessionMetadata = new Dictionary<string, object>(session.Metadata)
        };
    }
}

/// <summary>
/// Analytics data for a conversation session.
/// </summary>
public class SessionAnalytics
{
    public string SessionId { get; set; } = string.Empty;
    public DateTime StartTime { get; set; }
    public TimeSpan Duration { get; set; }
    public int TotalMessages { get; set; }
    public int UserMessages { get; set; }
    public int AssistantMessages { get; set; }
    public int EscalationCount { get; set; }
    public bool RequiresEscalation { get; set; }
    public int AttemptedStepsCount { get; set; }
    public string CurrentIssue { get; set; } = string.Empty;
}

/// <summary>
/// Summary of a conversation for escalation purposes.
/// </summary>
public class ConversationSummary
{
    public string SessionId { get; set; } = string.Empty;
    public DateTime StartTime { get; set; }
    public TimeSpan Duration { get; set; }
    public string CustomerIssue { get; set; } = string.Empty;
    public int MessageCount { get; set; }
    public List<string> AttemptedSteps { get; set; } = new();
    public string EscalationReason { get; set; } = string.Empty;
    public List<string> KeyUserMessages { get; set; } = new();
    public Dictionary<string, object> SessionMetadata { get; set; } = new();
}
