namespace TechSupportChatAgent.Models;

/// <summary>
/// Represents a chat message in the conversation.
/// </summary>
public class ChatMessage
{
    /// <summary>
    /// Unique identifier for the message.
    /// </summary>
    public string Id { get; set; } = Guid.NewGuid().ToString();
    
    /// <summary>
    /// Role of the message author.
    /// </summary>
    public ChatRole Role { get; set; }
    
    /// <summary>
    /// Content of the message.
    /// </summary>
    public string Content { get; set; } = string.Empty;
    
    /// <summary>
    /// Timestamp when the message was created.
    /// </summary>
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    
    /// <summary>
    /// Additional metadata for the message.
    /// </summary>
    public Dictionary<string, object> Metadata { get; set; } = new();
}

/// <summary>
/// Roles for chat participants.
/// </summary>
public enum ChatRole
{
    /// <summary>
    /// Message from the user.
    /// </summary>
    User,
    
    /// <summary>
    /// Message from the AI assistant/agent.
    /// </summary>
    Assistant,
    
    /// <summary>
    /// System message for context or instructions.
    /// </summary>
    System
}

/// <summary>
/// Represents the current state of a conversation session.
/// </summary>
public class ConversationSession
{
    /// <summary>
    /// Unique identifier for the session.
    /// </summary>
    public string SessionId { get; set; } = Guid.NewGuid().ToString();
    
    /// <summary>
    /// When the session started.
    /// </summary>
    public DateTime StartTime { get; set; } = DateTime.UtcNow;
    
    /// <summary>
    /// Current user issue being addressed.
    /// </summary>
    public string CurrentIssue { get; set; } = string.Empty;
    
    /// <summary>
    /// Number of escalation attempts in this session.
    /// </summary>
    public int EscalationCount { get; set; } = 0;
    
    /// <summary>
    /// Previous troubleshooting steps attempted.
    /// </summary>
    public List<string> PreviousSteps { get; set; } = new();
    
    /// <summary>
    /// Current conversation turn count.
    /// </summary>
    public int TurnCount { get; set; } = 0;
    
    /// <summary>
    /// Whether the session requires escalation.
    /// </summary>
    public bool RequiresEscalation { get; set; } = false;
    
    /// <summary>
    /// Additional session metadata.
    /// </summary>
    public Dictionary<string, object> Metadata { get; set; } = new();
}

/// <summary>
/// Response from the agent processing.
/// </summary>
public class AgentResponse
{
    /// <summary>
    /// The response text from the agent.
    /// </summary>
    public string ResponseText { get; set; } = string.Empty;
    
    /// <summary>
    /// Sources retrieved from the knowledge base.
    /// </summary>
    public List<string> RetrievedSources { get; set; } = new();
    
    /// <summary>
    /// Confidence score of the response.
    /// </summary>
    public double ConfidenceScore { get; set; } = 0.0;
    
    /// <summary>
    /// Whether the response indicates escalation is needed.
    /// </summary>
    public bool RequiresEscalation { get; set; } = false;
    
    /// <summary>
    /// Suggested actions for the user.
    /// </summary>
    public List<string> SuggestedActions { get; set; } = new();
    
    /// <summary>
    /// Additional metadata about the response.
    /// </summary>
    public Dictionary<string, object> Metadata { get; set; } = new();
}
