using Microsoft.Extensions.Logging;
using TechSupportChatAgent.Models;

namespace TechSupportChatAgent.Services;

/// <summary>
/// Service for handling escalation workflows and handoff to human agents.
/// </summary>
public class EscalationService
{
    private readonly ILogger<EscalationService> _logger;
    private readonly ConversationManager _conversationManager;
    private readonly List<EscalationTicket> _escalationQueue = new();

    public EscalationService(
        ILogger<EscalationService> logger,
        ConversationManager conversationManager)
    {
        _logger = logger;
        _conversationManager = conversationManager;
    }

    /// <summary>
    /// Initiates an escalation workflow for a conversation session.
    /// </summary>
    /// <param name="session">The conversation session to escalate.</param>
    /// <param name="reason">Optional reason for escalation.</param>
    /// <returns>The created escalation ticket.</returns>
    public async Task<EscalationTicket> InitiateEscalationAsync(
        ConversationSession session, 
        string? reason = null)
    {
        _logger.LogInformation("Initiating escalation for session {SessionId}", session.SessionId);

        // Mark session for escalation
        var escalationReason = reason ?? DetermineEscalationReason(session);
        _conversationManager.MarkForEscalation(session, escalationReason);

        // Create escalation ticket
        var ticket = await CreateEscalationTicketAsync(session, escalationReason);

        // Add to escalation queue
        _escalationQueue.Add(ticket);

        // Log escalation details
        _logger.LogInformation("Created escalation ticket {TicketId} for session {SessionId}: {Reason}",
            ticket.TicketId, session.SessionId, escalationReason);

        // In a real system, this would trigger notifications to human agents
        await NotifyHumanAgentsAsync(ticket);

        return ticket;
    }

    /// <summary>
    /// Creates an escalation ticket with conversation summary.
    /// </summary>
    private async Task<EscalationTicket> CreateEscalationTicketAsync(
        ConversationSession session, 
        string reason)
    {
        var summary = _conversationManager.CreateEscalationSummary(session.SessionId);
        var priority = DetermineTicketPriority(session, reason);

        var ticket = new EscalationTicket
        {
            TicketId = GenerateTicketId(),
            SessionId = session.SessionId,
            Priority = priority,
            Reason = reason,
            CustomerIssue = session.CurrentIssue,
            CreatedAt = DateTime.UtcNow,
            Status = EscalationStatus.Open,
            ConversationSummary = summary,
            EstimatedResponseTime = CalculateEstimatedResponseTime(priority)
        };

        await Task.CompletedTask; // Placeholder for async operations like database save
        return ticket;
    }

    /// <summary>
    /// Determines the reason for escalation based on session context.
    /// </summary>
    private string DetermineEscalationReason(ConversationSession session)
    {
        if (session.TurnCount > 20)
            return "Extended conversation without resolution";
        
        if (session.EscalationCount > 0)
            return "Multiple escalation attempts";
        
        if (session.PreviousSteps.Count > 5)
            return "Multiple troubleshooting attempts failed";
        
        return "Customer requested specialist assistance";
    }

    /// <summary>
    /// Determines the priority level for the escalation ticket.
    /// </summary>
    private TicketPriority DetermineTicketPriority(ConversationSession session, string reason)
    {
        // Check for high-priority keywords in the issue description
        var issue = session.CurrentIssue.ToLowerInvariant();
        
        if (issue.Contains("urgent") || issue.Contains("critical") || issue.Contains("down") || issue.Contains("error"))
            return TicketPriority.High;
        
        if (issue.Contains("slow") || issue.Contains("performance") || session.TurnCount > 15)
            return TicketPriority.Medium;
        
        return TicketPriority.Low;
    }

    /// <summary>
    /// Calculates estimated response time based on priority.
    /// </summary>
    private TimeSpan CalculateEstimatedResponseTime(TicketPriority priority)
    {
        return priority switch
        {
            TicketPriority.High => TimeSpan.FromMinutes(15),
            TicketPriority.Medium => TimeSpan.FromHours(2),
            TicketPriority.Low => TimeSpan.FromHours(8),
            _ => TimeSpan.FromHours(4)
        };
    }

    /// <summary>
    /// Generates a unique ticket ID.
    /// </summary>
    private string GenerateTicketId()
    {
        var timestamp = DateTime.UtcNow.ToString("yyyyMMddHHmmss");
        var random = new Random().Next(1000, 9999);
        return $"TS-{timestamp}-{random}";
    }

    /// <summary>
    /// Simulates notifying human agents about the escalation.
    /// </summary>
    private async Task NotifyHumanAgentsAsync(EscalationTicket ticket)
    {
        _logger.LogInformation("Notifying human agents about escalation ticket {TicketId}", ticket.TicketId);
        
        // In a real system, this would:
        // - Send notifications to available agents
        // - Update agent queue systems
        // - Send email/SMS alerts for high-priority tickets
        // - Update dashboards and monitoring systems
        
        await Task.Delay(100); // Simulate notification processing
        
        Console.WriteLine($"\n🚨 Escalation Alert");
        Console.WriteLine($"   Ticket ID: {ticket.TicketId}");
        Console.WriteLine($"   Priority: {ticket.Priority}");
        Console.WriteLine($"   Issue: {ticket.CustomerIssue}");
        Console.WriteLine($"   Estimated Response: {ticket.EstimatedResponseTime.TotalMinutes:F0} minutes");
    }

    /// <summary>
    /// Gets the current escalation queue.
    /// </summary>
    /// <returns>List of pending escalation tickets.</returns>
    public List<EscalationTicket> GetEscalationQueue()
    {
        return _escalationQueue.Where(t => t.Status == EscalationStatus.Open).ToList();
    }

    /// <summary>
    /// Gets an escalation ticket by ID.
    /// </summary>
    /// <param name="ticketId">The ticket ID.</param>
    /// <returns>The escalation ticket if found.</returns>
    public EscalationTicket? GetTicket(string ticketId)
    {
        return _escalationQueue.FirstOrDefault(t => t.TicketId == ticketId);
    }

    /// <summary>
    /// Updates the status of an escalation ticket.
    /// </summary>
    /// <param name="ticketId">The ticket ID.</param>
    /// <param name="status">The new status.</param>
    /// <param name="notes">Optional notes about the status change.</param>
    public async Task UpdateTicketStatusAsync(string ticketId, EscalationStatus status, string? notes = null)
    {
        var ticket = GetTicket(ticketId);
        if (ticket != null)
        {
            var oldStatus = ticket.Status;
            ticket.Status = status;
            ticket.LastUpdated = DateTime.UtcNow;
            
            if (!string.IsNullOrEmpty(notes))
            {
                ticket.AgentNotes.Add($"{DateTime.UtcNow:yyyy-MM-dd HH:mm:ss} - {notes}");
            }
            
            _logger.LogInformation("Updated ticket {TicketId} status from {OldStatus} to {NewStatus}",
                ticketId, oldStatus, status);
        }
        
        await Task.CompletedTask;
    }

    /// <summary>
    /// Assigns an escalation ticket to a human agent.
    /// </summary>
    /// <param name="ticketId">The ticket ID.</param>
    /// <param name="agentId">The agent ID.</param>
    /// <param name="agentName">The agent name.</param>
    public async Task AssignTicketAsync(string ticketId, string agentId, string agentName)
    {
        var ticket = GetTicket(ticketId);
        if (ticket != null)
        {
            ticket.AssignedAgentId = agentId;
            ticket.AssignedAgentName = agentName;
            ticket.Status = EscalationStatus.InProgress;
            ticket.LastUpdated = DateTime.UtcNow;
            ticket.AgentNotes.Add($"{DateTime.UtcNow:yyyy-MM-dd HH:mm:ss} - Assigned to {agentName}");
            
            _logger.LogInformation("Assigned ticket {TicketId} to agent {AgentName} ({AgentId})",
                ticketId, agentName, agentId);
        }
        
        await Task.CompletedTask;
    }

    /// <summary>
    /// Provides escalation statistics for monitoring.
    /// </summary>
    /// <returns>Escalation statistics.</returns>
    public EscalationStatistics GetEscalationStatistics()
    {
        var now = DateTime.UtcNow;
        var today = now.Date;
        
        var todayTickets = _escalationQueue.Where(t => t.CreatedAt.Date == today).ToList();
        var openTickets = _escalationQueue.Where(t => t.Status == EscalationStatus.Open).ToList();
        var closedTickets = _escalationQueue.Where(t => t.Status == EscalationStatus.Resolved).ToList();
        
        return new EscalationStatistics
        {
            TotalTickets = _escalationQueue.Count,
            OpenTickets = openTickets.Count,
            InProgressTickets = _escalationQueue.Count(t => t.Status == EscalationStatus.InProgress),
            ResolvedTickets = closedTickets.Count,
            TodayTickets = todayTickets.Count,
            HighPriorityTickets = openTickets.Count(t => t.Priority == TicketPriority.High),
            AverageResponseTime = closedTickets.Any() 
                ? TimeSpan.FromTicks((long)closedTickets.Average(t => (t.LastUpdated - t.CreatedAt).Ticks))
                : TimeSpan.Zero
        };
    }
}

/// <summary>
/// Represents an escalation ticket for human agent assistance.
/// </summary>
public class EscalationTicket
{
    public string TicketId { get; set; } = string.Empty;
    public string SessionId { get; set; } = string.Empty;
    public TicketPriority Priority { get; set; }
    public string Reason { get; set; } = string.Empty;
    public string CustomerIssue { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; }
    public DateTime LastUpdated { get; set; }
    public EscalationStatus Status { get; set; }
    public string AssignedAgentId { get; set; } = string.Empty;
    public string AssignedAgentName { get; set; } = string.Empty;
    public ConversationSummary ConversationSummary { get; set; } = new();
    public TimeSpan EstimatedResponseTime { get; set; }
    public List<string> AgentNotes { get; set; } = new();
}

/// <summary>
/// Priority levels for escalation tickets.
/// </summary>
public enum TicketPriority
{
    Low,
    Medium,
    High,
    Critical
}

/// <summary>
/// Status options for escalation tickets.
/// </summary>
public enum EscalationStatus
{
    Open,
    InProgress,
    Resolved,
    Cancelled
}

/// <summary>
/// Statistics about escalation activity.
/// </summary>
public class EscalationStatistics
{
    public int TotalTickets { get; set; }
    public int OpenTickets { get; set; }
    public int InProgressTickets { get; set; }
    public int ResolvedTickets { get; set; }
    public int TodayTickets { get; set; }
    public int HighPriorityTickets { get; set; }
    public TimeSpan AverageResponseTime { get; set; }
}
