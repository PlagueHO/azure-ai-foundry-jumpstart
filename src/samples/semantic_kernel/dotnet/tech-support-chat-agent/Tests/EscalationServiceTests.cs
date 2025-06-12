using Microsoft.Extensions.Logging;
using Moq;
using Xunit;
using TechSupportChatAgent.Models;
using TechSupportChatAgent.Services;

namespace TechSupportChatAgent.Tests.Services;

public class EscalationServiceTests
{
    private readonly Mock<ILogger<EscalationService>> _loggerMock;
    private readonly Mock<ConversationManager> _conversationManagerMock;
    private readonly EscalationService _escalationService;

    public EscalationServiceTests()
    {
        _loggerMock = new Mock<ILogger<EscalationService>>();
        _conversationManagerMock = new Mock<ConversationManager>(Mock.Of<ILogger<ConversationManager>>());
        _escalationService = new EscalationService(_loggerMock.Object, _conversationManagerMock.Object);
    }

    [Fact]
    public async Task InitiateEscalationAsync_ShouldCreateTicket()
    {
        // Arrange
        var session = new ConversationSession
        {
            SessionId = "test-session",
            CurrentIssue = "Computer won't start",
            TurnCount = 5
        };

        var conversationSummary = new ConversationSummary
        {
            SessionId = session.SessionId,
            CustomerIssue = session.CurrentIssue,
            MessageCount = 10
        };

        _conversationManagerMock
            .Setup(x => x.CreateEscalationSummary(session.SessionId))
            .Returns(conversationSummary);

        // Act
        var ticket = await _escalationService.InitiateEscalationAsync(session);

        // Assert
        Assert.NotNull(ticket);
        Assert.NotEmpty(ticket.TicketId);
        Assert.Equal(session.SessionId, ticket.SessionId);
        Assert.Equal(session.CurrentIssue, ticket.CustomerIssue);
        Assert.Equal(EscalationStatus.Open, ticket.Status);
        Assert.True(ticket.CreatedAt > DateTime.MinValue);
    }

    [Fact]
    public async Task InitiateEscalationAsync_WithCustomReason_ShouldUseProvidedReason()
    {
        // Arrange
        var session = new ConversationSession
        {
            SessionId = "test-session",
            CurrentIssue = "Network issue"
        };

        var customReason = "Customer specifically requested escalation";
        var conversationSummary = new ConversationSummary { SessionId = session.SessionId };

        _conversationManagerMock
            .Setup(x => x.CreateEscalationSummary(session.SessionId))
            .Returns(conversationSummary);

        // Act
        var ticket = await _escalationService.InitiateEscalationAsync(session, customReason);

        // Assert
        Assert.Equal(customReason, ticket.Reason);
    }

    [Fact]
    public void GetEscalationQueue_ShouldReturnOnlyOpenTickets()
    {
        // Arrange
        var session1 = new ConversationSession { SessionId = "session1", CurrentIssue = "Issue 1" };
        var session2 = new ConversationSession { SessionId = "session2", CurrentIssue = "Issue 2" };

        var conversationSummary = new ConversationSummary();
        _conversationManagerMock
            .Setup(x => x.CreateEscalationSummary(It.IsAny<string>()))
            .Returns(conversationSummary);

        // Act - Create tickets and close one
        var ticket1 = _escalationService.InitiateEscalationAsync(session1).Result;
        var ticket2 = _escalationService.InitiateEscalationAsync(session2).Result;
        _escalationService.UpdateTicketStatusAsync(ticket1.TicketId, EscalationStatus.Resolved).Wait();

        var openTickets = _escalationService.GetEscalationQueue();

        // Assert
        Assert.Single(openTickets);
        Assert.Equal(ticket2.TicketId, openTickets[0].TicketId);
    }

    [Fact]
    public async Task UpdateTicketStatusAsync_ShouldUpdateTicketProperties()
    {
        // Arrange
        var session = new ConversationSession { SessionId = "test-session", CurrentIssue = "Test issue" };
        var conversationSummary = new ConversationSummary { SessionId = session.SessionId };

        _conversationManagerMock
            .Setup(x => x.CreateEscalationSummary(session.SessionId))
            .Returns(conversationSummary);

        var ticket = await _escalationService.InitiateEscalationAsync(session);
        var notes = "Ticket resolved successfully";

        // Act
        await _escalationService.UpdateTicketStatusAsync(ticket.TicketId, EscalationStatus.Resolved, notes);

        // Assert
        var updatedTicket = _escalationService.GetTicket(ticket.TicketId);
        Assert.NotNull(updatedTicket);
        Assert.Equal(EscalationStatus.Resolved, updatedTicket.Status);
        Assert.Contains(notes, updatedTicket.AgentNotes[0]);
        Assert.True(updatedTicket.LastUpdated > updatedTicket.CreatedAt);
    }

    [Fact]
    public async Task AssignTicketAsync_ShouldAssignTicketToAgent()
    {
        // Arrange
        var session = new ConversationSession { SessionId = "test-session", CurrentIssue = "Test issue" };
        var conversationSummary = new ConversationSummary { SessionId = session.SessionId };

        _conversationManagerMock
            .Setup(x => x.CreateEscalationSummary(session.SessionId))
            .Returns(conversationSummary);

        var ticket = await _escalationService.InitiateEscalationAsync(session);
        var agentId = "agent123";
        var agentName = "John Smith";

        // Act
        await _escalationService.AssignTicketAsync(ticket.TicketId, agentId, agentName);

        // Assert
        var assignedTicket = _escalationService.GetTicket(ticket.TicketId);
        Assert.NotNull(assignedTicket);
        Assert.Equal(agentId, assignedTicket.AssignedAgentId);
        Assert.Equal(agentName, assignedTicket.AssignedAgentName);
        Assert.Equal(EscalationStatus.InProgress, assignedTicket.Status);
        Assert.Single(assignedTicket.AgentNotes);
        Assert.Contains(agentName, assignedTicket.AgentNotes[0]);
    }

    [Fact]
    public void GetTicket_WithValidId_ShouldReturnTicket()
    {
        // Arrange
        var session = new ConversationSession { SessionId = "test-session", CurrentIssue = "Test issue" };
        var conversationSummary = new ConversationSummary { SessionId = session.SessionId };

        _conversationManagerMock
            .Setup(x => x.CreateEscalationSummary(session.SessionId))
            .Returns(conversationSummary);

        var ticket = _escalationService.InitiateEscalationAsync(session).Result;

        // Act
        var retrievedTicket = _escalationService.GetTicket(ticket.TicketId);

        // Assert
        Assert.NotNull(retrievedTicket);
        Assert.Equal(ticket.TicketId, retrievedTicket.TicketId);
    }

    [Fact]
    public void GetTicket_WithInvalidId_ShouldReturnNull()
    {
        // Act
        var ticket = _escalationService.GetTicket("non-existent-ticket");

        // Assert
        Assert.Null(ticket);
    }

    [Fact]
    public void GetEscalationStatistics_ShouldReturnCorrectStats()
    {
        // Arrange
        var session1 = new ConversationSession { SessionId = "session1", CurrentIssue = "Issue 1" };
        var session2 = new ConversationSession { SessionId = "session2", CurrentIssue = "Issue 2" };

        var conversationSummary = new ConversationSummary();
        _conversationManagerMock
            .Setup(x => x.CreateEscalationSummary(It.IsAny<string>()))
            .Returns(conversationSummary);

        // Create tickets with different statuses
        var ticket1 = _escalationService.InitiateEscalationAsync(session1).Result;
        var ticket2 = _escalationService.InitiateEscalationAsync(session2).Result;
        _escalationService.UpdateTicketStatusAsync(ticket1.TicketId, EscalationStatus.Resolved).Wait();
        _escalationService.AssignTicketAsync(ticket2.TicketId, "agent1", "Agent 1").Wait();

        // Act
        var stats = _escalationService.GetEscalationStatistics();

        // Assert
        Assert.Equal(2, stats.TotalTickets);
        Assert.Equal(0, stats.OpenTickets);
        Assert.Equal(1, stats.InProgressTickets);
        Assert.Equal(1, stats.ResolvedTickets);
    }

    [Theory]
    [InlineData("urgent issue", TicketPriority.High)]
    [InlineData("critical system down", TicketPriority.High)]
    [InlineData("slow performance", TicketPriority.Medium)]
    [InlineData("general question", TicketPriority.Low)]
    public async Task InitiateEscalationAsync_ShouldSetCorrectPriority(string issue, TicketPriority expectedPriority)
    {
        // Arrange
        var session = new ConversationSession
        {
            SessionId = "test-session",
            CurrentIssue = issue
        };

        var conversationSummary = new ConversationSummary { SessionId = session.SessionId };
        _conversationManagerMock
            .Setup(x => x.CreateEscalationSummary(session.SessionId))
            .Returns(conversationSummary);

        // Act
        var ticket = await _escalationService.InitiateEscalationAsync(session);

        // Assert
        Assert.Equal(expectedPriority, ticket.Priority);
    }
}
