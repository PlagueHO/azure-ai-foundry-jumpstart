using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Microsoft.SemanticKernel.Agents.AzureAI;
using TechSupportChatAgent.Configuration;
using TechSupportChatAgent.Models;

#pragma warning disable SKEXP0001 // Type is for evaluation purposes only
#pragma warning disable SKEXP0110 // Type is for evaluation purposes only

namespace TechSupportChatAgent.Services;

/// <summary>
/// Service for managing interactive chat sessions with the tech support agent.
/// </summary>
public class ChatService
{
    private readonly ILogger<ChatService> _logger;
    private readonly AgentSetupService _agentSetupService;
    private readonly ConversationManager _conversationManager;
    private readonly EscalationService _escalationService;
    private readonly AgentFrameworkConfiguration _agentConfig;

    public ChatService(
        ILogger<ChatService> logger,
        AgentSetupService agentSetupService,
        ConversationManager conversationManager,
        EscalationService escalationService,
        IConfiguration configuration)
    {
        _logger = logger;
        _agentSetupService = agentSetupService;
        _conversationManager = conversationManager;
        _escalationService = escalationService;
        
        _agentConfig = new AgentFrameworkConfiguration();
        configuration.GetSection(AgentFrameworkConfiguration.SectionName).Bind(_agentConfig);
    }

    /// <summary>
    /// Starts an interactive chat session with the tech support agent.
    /// </summary>
    /// <param name="cancellationToken">Cancellation token.</param>
    public async Task StartInteractiveChatAsync(CancellationToken cancellationToken = default)
    {
        _logger.LogInformation("Starting interactive tech support chat session");
        
        try
        {
            // Initialize the agent
            var agent = await _agentSetupService.CreateAgentAsync(cancellationToken);
            
            // Create a new conversation session
            var session = _conversationManager.CreateNewSession();
            
            // Display welcome message
            DisplayWelcomeMessage();
            
            // Main chat loop
            await RunChatLoopAsync(agent, session, cancellationToken);
        }
        catch (OperationCanceledException)
        {
            _logger.LogInformation("Chat session was cancelled");
            Console.WriteLine("\n🔄 Chat session ended. Thank you for using Tech Support!");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during chat session");
            Console.WriteLine($"\n❌ An error occurred: {ex.Message}");
            throw;
        }
    }

    /// <summary>
    /// Displays the welcome message to the user.
    /// </summary>
    private void DisplayWelcomeMessage()
    {
        Console.Clear();
        Console.WriteLine("🔧 Tech Support Chat Agent");
        Console.WriteLine("═══════════════════════════");
        Console.WriteLine();
        Console.WriteLine("Welcome! I'm here to help you with technical issues.");
        Console.WriteLine("Please describe your problem, and I'll do my best to assist you.");
        Console.WriteLine();
        Console.WriteLine("Commands:");
        Console.WriteLine("  • Type 'exit' to end the session");
        Console.WriteLine("  • Type 'escalate' to request human assistance");
        Console.WriteLine("  • Type 'help' for more information");
        Console.WriteLine();
        Console.WriteLine("Let's get started! What technical issue are you experiencing?");
        Console.WriteLine();
    }

    /// <summary>
    /// Runs the main chat interaction loop.
    /// </summary>
    private async Task RunChatLoopAsync(
        AzureAIAgent? agent, 
        ConversationSession session, 
        CancellationToken cancellationToken)
    {
        while (!cancellationToken.IsCancellationRequested)
        {
            try
            {
                // Get user input
                Console.Write("You: ");
                var userInput = Console.ReadLine()?.Trim();
                
                if (string.IsNullOrEmpty(userInput))
                    continue;

                // Handle special commands
                if (await HandleSpecialCommandsAsync(userInput, session))
                    break;

                // Process the user message
                await ProcessUserMessageAsync(agent, session, userInput, cancellationToken);
                
                // Check for automatic escalation conditions
                await CheckEscalationConditionsAsync(session);
            }
            catch (OperationCanceledException)
            {
                break;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error processing user message");
                Console.WriteLine($"❌ Sorry, I encountered an error: {ex.Message}");
                Console.WriteLine("Please try again or type 'escalate' for human assistance.");
            }
        }
    }

    /// <summary>
    /// Handles special user commands like exit, escalate, help.
    /// </summary>
    /// <returns>True if the session should end.</returns>
    private async Task<bool> HandleSpecialCommandsAsync(string input, ConversationSession session)
    {
        switch (input.ToLowerInvariant())
        {
            case "exit":
            case "quit":
            case "bye":
                await DisplaySessionSummaryAsync(session);
                return true;

            case "escalate":
                await _escalationService.InitiateEscalationAsync(session);
                Console.WriteLine("🔄 Your request has been escalated to a human specialist.");
                Console.WriteLine("Thank you for using Tech Support!");
                return true;

            case "help":
                DisplayHelpMessage();
                return false;

            case "status":
                DisplaySessionStatus(session);
                return false;

            default:
                return false;
        }
    }

    /// <summary>
    /// Processes a user message and generates an agent response.
    /// </summary>
    private async Task ProcessUserMessageAsync(
        AzureAIAgent? agent,
        ConversationSession session,
        string userInput,
        CancellationToken cancellationToken)
    {
        // Add user message to conversation
        var userMessage = new ChatMessage
        {
            Role = ChatRole.User,
            Content = userInput
        };
        
        _conversationManager.AddMessage(session, userMessage);
        session.TurnCount++;

        // Update session context
        if (session.TurnCount == 1)
        {
            session.CurrentIssue = userInput;
        }

        Console.WriteLine();
        Console.Write("🔧 Agent: ");
        
        // Since the agent creation is not yet implemented, provide a mock response
        if (agent == null)
        {
            var mockResponse = await GenerateMockResponseAsync(session, userInput);
            Console.WriteLine(mockResponse.ResponseText);
            
            if (mockResponse.SuggestedActions.Any())
            {
                Console.WriteLine("\nSuggested actions:");
                foreach (var action in mockResponse.SuggestedActions)
                {
                    Console.WriteLine($"  • {action}");
                }
            }
            
            // Add agent response to conversation
            var agentMessage = new ChatMessage
            {
                Role = ChatRole.Assistant,
                Content = mockResponse.ResponseText
            };
            _conversationManager.AddMessage(session, agentMessage);
        }
        else
        {
            // TODO: Implement actual agent interaction when SDK is available
            // This would involve:
            // 1. Creating a thread if needed
            // 2. Adding the user message to the thread
            // 3. Running the agent to generate a response
            // 4. Retrieving the response and any file search results
            
            Console.WriteLine("Agent interaction not yet implemented - using mock response");
        }
        
        Console.WriteLine();
    }

    /// <summary>
    /// Generates a mock response for demonstration purposes.
    /// </summary>
    private async Task<AgentResponse> GenerateMockResponseAsync(ConversationSession session, string userInput)
    {
        await Task.Delay(500); // Simulate processing time
        
        var response = new AgentResponse();
        
        // Simple keyword-based mock responses
        var lowerInput = userInput.ToLowerInvariant();
        
        if (lowerInput.Contains("password") || lowerInput.Contains("login"))
        {
            response.ResponseText = "I can help you with password and login issues. Let me suggest some common troubleshooting steps.";
            response.SuggestedActions = new List<string>
            {
                "Try resetting your password using the 'Forgot Password' link",
                "Clear your browser cache and cookies",
                "Try logging in from an incognito/private browsing window",
                "Check if Caps Lock is enabled"
            };
            response.ConfidenceScore = 0.85;
        }
        else if (lowerInput.Contains("slow") || lowerInput.Contains("performance"))
        {
            response.ResponseText = "I understand you're experiencing performance issues. Let's try some optimization steps.";
            response.SuggestedActions = new List<string>
            {
                "Restart your device to clear temporary files",
                "Close unnecessary programs and browser tabs",
                "Check available disk space (should have at least 15% free)",
                "Run a disk cleanup utility"
            };
            response.ConfidenceScore = 0.80;
        }
        else if (lowerInput.Contains("internet") || lowerInput.Contains("connection") || lowerInput.Contains("wifi"))
        {
            response.ResponseText = "Network connectivity issues can be frustrating. Let's diagnose the problem step by step.";
            response.SuggestedActions = new List<string>
            {
                "Check if other devices can connect to the same network",
                "Restart your modem and router (unplug for 30 seconds)",
                "Forget and reconnect to the WiFi network",
                "Run Windows Network Troubleshooter"
            };
            response.ConfidenceScore = 0.90;
        }
        else if (session.TurnCount > _agentConfig.EscalationThreshold)
        {
            response.ResponseText = "I notice we've been working on this issue for a while. Would you like me to escalate this to a specialist who can provide more detailed assistance?";
            response.RequiresEscalation = true;
            response.ConfidenceScore = 0.70;
        }
        else
        {
            response.ResponseText = "I understand your concern. Could you provide more specific details about the issue you're experiencing? For example, when did it start, what error messages you see, and what steps you've already tried?";
            response.SuggestedActions = new List<string>
            {
                "Describe any error messages you're seeing",
                "Mention when the problem first started",
                "List any troubleshooting steps you've already attempted"
            };
            response.ConfidenceScore = 0.60;
        }
        
        // Add some mock retrieved sources
        response.RetrievedSources = new List<string>
        {
            "Tech Support Knowledge Base - Common Issues",
            "Troubleshooting Guide v2.1",
            "FAQ: User Account Problems"
        };
        
        return response;
    }

    /// <summary>
    /// Checks if escalation conditions are met and handles accordingly.
    /// </summary>
    private async Task CheckEscalationConditionsAsync(ConversationSession session)
    {
        if (session.TurnCount >= _agentConfig.MaxConversationTurns)
        {
            Console.WriteLine("\n⚠️ This conversation has reached the maximum length.");
            Console.WriteLine("I recommend escalating to a human specialist for further assistance.");
            Console.WriteLine("Type 'escalate' to connect with a specialist, or 'exit' to end the session.");
        }
        else if (session.EscalationCount >= _agentConfig.EscalationThreshold)
        {
            await _escalationService.InitiateEscalationAsync(session);
        }
    }

    /// <summary>
    /// Displays help information to the user.
    /// </summary>
    private void DisplayHelpMessage()
    {
        Console.WriteLine("\n📋 Help Information");
        Console.WriteLine("═══════════════════");
        Console.WriteLine("Available commands:");
        Console.WriteLine("  • help     - Show this help message");
        Console.WriteLine("  • status   - Show current session information");
        Console.WriteLine("  • escalate - Request human specialist assistance");
        Console.WriteLine("  • exit     - End the chat session");
        Console.WriteLine();
        Console.WriteLine("Tips for better assistance:");
        Console.WriteLine("  • Be specific about your problem");
        Console.WriteLine("  • Include error messages if any");
        Console.WriteLine("  • Mention what you've already tried");
        Console.WriteLine("  • Describe when the problem started");
        Console.WriteLine();
    }

    /// <summary>
    /// Displays current session status.
    /// </summary>
    private void DisplaySessionStatus(ConversationSession session)
    {
        Console.WriteLine($"\n📊 Session Status");
        Console.WriteLine("═════════════════");
        Console.WriteLine($"Session ID: {session.SessionId}");
        Console.WriteLine($"Started: {session.StartTime:yyyy-MM-dd HH:mm:ss} UTC");
        Console.WriteLine($"Current Issue: {session.CurrentIssue}");
        Console.WriteLine($"Turn Count: {session.TurnCount}");
        Console.WriteLine($"Escalation Count: {session.EscalationCount}");
        Console.WriteLine($"Duration: {DateTime.UtcNow - session.StartTime:hh\\:mm\\:ss}");
        Console.WriteLine();
    }

    /// <summary>
    /// Displays session summary when ending the chat.
    /// </summary>
    private async Task DisplaySessionSummaryAsync(ConversationSession session)
    {
        Console.WriteLine("\n📋 Session Summary");
        Console.WriteLine("═══════════════════");
        Console.WriteLine($"Session Duration: {DateTime.UtcNow - session.StartTime:hh\\:mm\\:ss}");
        Console.WriteLine($"Total Messages: {session.TurnCount * 2}"); // User + Agent messages
        Console.WriteLine($"Issue: {session.CurrentIssue}");
        
        if (session.PreviousSteps.Any())
        {
            Console.WriteLine("Steps Attempted:");
            foreach (var step in session.PreviousSteps)
            {
                Console.WriteLine($"  • {step}");
            }
        }
        
        Console.WriteLine("\nThank you for using Tech Support Chat Agent!");
        
        await Task.CompletedTask;
    }
}
