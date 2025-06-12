using Microsoft.Extensions.Logging;
using Moq;
using Xunit;
using TechSupportChatAgent.Models;
using TechSupportChatAgent.Services;

namespace TechSupportChatAgent.Tests.Services;

public class ConversationManagerTests
{
    private readonly Mock<ILogger<ConversationManager>> _loggerMock;
    private readonly ConversationManager _conversationManager;

    public ConversationManagerTests()
    {
        _loggerMock = new Mock<ILogger<ConversationManager>>();
        _conversationManager = new ConversationManager(_loggerMock.Object);
    }

    [Fact]
    public void CreateNewSession_ShouldReturnValidSession()
    {
        // Act
        var session = _conversationManager.CreateNewSession();

        // Assert
        Assert.NotNull(session);
        Assert.NotEmpty(session.SessionId);
        Assert.True(session.StartTime > DateTime.MinValue);
        Assert.Equal(0, session.TurnCount);
        Assert.Equal(0, session.EscalationCount);
        Assert.False(session.RequiresEscalation);
        Assert.Empty(session.PreviousSteps);
    }

    [Fact]
    public void GetSession_WithValidId_ShouldReturnSession()
    {
        // Arrange
        var session = _conversationManager.CreateNewSession();

        // Act
        var retrievedSession = _conversationManager.GetSession(session.SessionId);

        // Assert
        Assert.NotNull(retrievedSession);
        Assert.Equal(session.SessionId, retrievedSession.SessionId);
    }

    [Fact]
    public void GetSession_WithInvalidId_ShouldReturnNull()
    {
        // Act
        var session = _conversationManager.GetSession("non-existent-id");

        // Assert
        Assert.Null(session);
    }

    [Fact]
    public void AddMessage_ShouldAddMessageToHistory()
    {
        // Arrange
        var session = _conversationManager.CreateNewSession();
        var message = new ChatMessage
        {
            Role = ChatRole.User,
            Content = "Test message"
        };

        // Act
        _conversationManager.AddMessage(session, message);
        var history = _conversationManager.GetConversationHistory(session.SessionId);

        // Assert
        Assert.Single(history);
        Assert.Equal(message.Content, history[0].Content);
        Assert.Equal(message.Role, history[0].Role);
    }

    [Fact]
    public void GetRecentMessages_ShouldReturnCorrectCount()
    {
        // Arrange
        var session = _conversationManager.CreateNewSession();
        
        // Add multiple messages
        for (int i = 0; i < 15; i++)
        {
            var message = new ChatMessage
            {
                Role = i % 2 == 0 ? ChatRole.User : ChatRole.Assistant,
                Content = $"Message {i}"
            };
            _conversationManager.AddMessage(session, message);
        }

        // Act
        var recentMessages = _conversationManager.GetRecentMessages(session.SessionId, 10);

        // Assert
        Assert.Equal(10, recentMessages.Count);
        Assert.Equal("Message 14", recentMessages.Last().Content); // Most recent message
    }

    [Fact]
    public void AddAttemptedStep_ShouldAddUniqueStep()
    {
        // Arrange
        var session = _conversationManager.CreateNewSession();
        var step = "Restart the computer";

        // Act
        _conversationManager.AddAttemptedStep(session, step);
        _conversationManager.AddAttemptedStep(session, step); // Try adding same step twice

        // Assert
        Assert.Single(session.PreviousSteps);
        Assert.Equal(step, session.PreviousSteps[0]);
    }

    [Fact]
    public void MarkForEscalation_ShouldUpdateSessionProperties()
    {
        // Arrange
        var session = _conversationManager.CreateNewSession();
        var reason = "Customer request";

        // Act
        _conversationManager.MarkForEscalation(session, reason);

        // Assert
        Assert.True(session.RequiresEscalation);
        Assert.Equal(1, session.EscalationCount);
        Assert.Equal(reason, session.Metadata["escalation_reason"]);
        Assert.True(session.Metadata.ContainsKey("escalation_timestamp"));
    }

    [Fact]
    public void GetSessionAnalytics_ShouldReturnCorrectData()
    {
        // Arrange
        var session = _conversationManager.CreateNewSession();
        session.CurrentIssue = "Test issue";
        
        // Add some messages
        _conversationManager.AddMessage(session, new ChatMessage { Role = ChatRole.User, Content = "User msg 1" });
        _conversationManager.AddMessage(session, new ChatMessage { Role = ChatRole.Assistant, Content = "Agent msg 1" });
        _conversationManager.AddMessage(session, new ChatMessage { Role = ChatRole.User, Content = "User msg 2" });

        // Act
        var analytics = _conversationManager.GetSessionAnalytics(session.SessionId);

        // Assert
        Assert.Equal(session.SessionId, analytics.SessionId);
        Assert.Equal(3, analytics.TotalMessages);
        Assert.Equal(2, analytics.UserMessages);
        Assert.Equal(1, analytics.AssistantMessages);
        Assert.Equal("Test issue", analytics.CurrentIssue);
    }

    [Fact]
    public void CreateEscalationSummary_ShouldReturnValidSummary()
    {
        // Arrange
        var session = _conversationManager.CreateNewSession();
        session.CurrentIssue = "Computer won't start";
        session.PreviousSteps.Add("Checked power cable");
        session.PreviousSteps.Add("Tried different outlet");
        
        _conversationManager.AddMessage(session, new ChatMessage { Role = ChatRole.User, Content = "My computer won't turn on" });
        _conversationManager.AddMessage(session, new ChatMessage { Role = ChatRole.Assistant, Content = "Let me help you troubleshoot" });
        _conversationManager.MarkForEscalation(session, "Multiple failed attempts");

        // Act
        var summary = _conversationManager.CreateEscalationSummary(session.SessionId);

        // Assert
        Assert.Equal(session.SessionId, summary.SessionId);
        Assert.Equal("Computer won't start", summary.CustomerIssue);
        Assert.Equal(2, summary.MessageCount);
        Assert.Equal(2, summary.AttemptedSteps.Count);
        Assert.Equal("Multiple failed attempts", summary.EscalationReason);
        Assert.Single(summary.KeyUserMessages);
    }

    [Fact]
    public void EndSession_ShouldRemoveFromActiveSessions()
    {
        // Arrange
        var session = _conversationManager.CreateNewSession();
        var sessionId = session.SessionId;

        // Act
        _conversationManager.EndSession(sessionId);

        // Assert
        var retrievedSession = _conversationManager.GetSession(sessionId);
        Assert.Null(retrievedSession);
    }

    [Fact]
    public void GetActiveSessionIds_ShouldReturnCorrectCount()
    {
        // Arrange
        var session1 = _conversationManager.CreateNewSession();
        var session2 = _conversationManager.CreateNewSession();

        // Act
        var activeIds = _conversationManager.GetActiveSessionIds();

        // Assert
        Assert.Equal(2, activeIds.Count);
        Assert.Contains(session1.SessionId, activeIds);
        Assert.Contains(session2.SessionId, activeIds);
    }
}
