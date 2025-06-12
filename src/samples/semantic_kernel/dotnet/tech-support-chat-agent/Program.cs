using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using System.CommandLine;
using TechSupportChatAgent.Configuration;
using TechSupportChatAgent.Services;
using TechSupportChatAgent.Models;

namespace TechSupportChatAgent;

/// <summary>
/// Main entry point for the Tech Support Chat Agent application.
/// </summary>
public class Program
{
    private static readonly CancellationTokenSource _cancellationTokenSource = new();
    
    public static async Task<int> Main(string[] args)
    {
        // Handle Ctrl+C gracefully
        Console.CancelKeyPress += (_, e) =>
        {
            e.Cancel = true;
            _cancellationTokenSource.Cancel();
        };

        var rootCommand = new RootCommand("Tech Support Chat Agent - Azure AI Foundry Semantic Kernel Sample")
        {
            CreateChatCommand(),
            CreateValidateCommand(),
            CreateSetupCommand()
        };

        return await rootCommand.InvokeAsync(args);
    }

    /// <summary>
    /// Creates the interactive chat command.
    /// </summary>
    private static Command CreateChatCommand()
    {
        var chatCommand = new Command("chat", "Start an interactive tech support chat session");
        
        chatCommand.SetHandler(async () =>
        {
            var host = CreateHost();
            var chatService = host.Services.GetRequiredService<ChatService>();
            var logger = host.Services.GetRequiredService<ILogger<Program>>();
            
            try
            {
                await chatService.StartInteractiveChatAsync(_cancellationTokenSource.Token);
            }
            catch (OperationCanceledException)
            {
                logger.LogInformation("Chat session cancelled by user");
            }
            catch (Exception ex)
            {
                logger.LogError(ex, "Error during chat session");
                Environment.ExitCode = 1;
            }
        });

        return chatCommand;
    }    /// <summary>
    /// Creates the configuration validation command.
    /// </summary>
    private static Command CreateValidateCommand()
    {
        var validateCommand = new Command("validate", "Validate the application configuration");
        
        validateCommand.SetHandler(async () =>
        {
            var host = CreateHost();
            var agentSetupService = host.Services.GetRequiredService<AgentSetupService>();
            var logger = host.Services.GetRequiredService<ILogger<Program>>();
            
            try
            {
                if (agentSetupService.ValidateConfiguration())
                {
                    logger.LogInformation("✅ Configuration validation successful!");
                    Console.WriteLine("Configuration is valid and ready for use.");
                }
                else
                {
                    logger.LogError("❌ Configuration validation failed");
                    Console.WriteLine("Configuration validation failed. Check the logs for details.");
                    Environment.ExitCode = 1;
                }
            }
            catch (Exception ex)
            {
                logger.LogError(ex, "Error during configuration validation");
                Console.WriteLine($"Validation error: {ex.Message}");
                Environment.ExitCode = 1;
            }

            await Task.CompletedTask;
        });

        return validateCommand;
    }

    /// <summary>
    /// Creates the agent setup command.
    /// </summary>
    private static Command CreateSetupCommand()
    {
        var setupCommand = new Command("setup", "Set up the Azure AI Agent (placeholder for future implementation)");
        
        setupCommand.SetHandler(async () =>
        {
            var host = CreateHost();
            var agentSetupService = host.Services.GetRequiredService<AgentSetupService>();
            var logger = host.Services.GetRequiredService<ILogger<Program>>();
            
            try
            {
                logger.LogInformation("Setting up Azure AI Agent...");
                var agent = await agentSetupService.CreateAgentAsync(_cancellationTokenSource.Token);
                
                if (agent != null)
                {
                    logger.LogInformation("✅ Agent setup completed successfully!");
                    Console.WriteLine("Agent is ready for use.");
                }
                else
                {
                    logger.LogWarning("⚠️ Agent setup not yet implemented");
                    Console.WriteLine("Agent setup is currently a placeholder. Implementation pending Azure AI Foundry SDK updates.");
                }
            }
            catch (Exception ex)
            {
                logger.LogError(ex, "Error during agent setup");
                Console.WriteLine($"Setup error: {ex.Message}");
                Environment.ExitCode = 1;
            }
        });

        return setupCommand;
    }

    /// <summary>
    /// Creates and configures the application host.
    /// </summary>
    private static IHost CreateHost()
    {
        var builder = Host.CreateDefaultBuilder()
            .ConfigureAppConfiguration((context, config) =>
            {
                config.AddJsonFile("appsettings.json", optional: false, reloadOnChange: true)
                      .AddEnvironmentVariables()
                      .AddUserSecrets<Program>();
            })
            .ConfigureServices((context, services) =>
            {
                // Register configuration
                services.Configure<AzureAIConfiguration>(
                    context.Configuration.GetSection(AzureAIConfiguration.SectionName));
                services.Configure<AgentFrameworkConfiguration>(
                    context.Configuration.GetSection(AgentFrameworkConfiguration.SectionName));

                // Register services
                services.AddSingleton<AgentSetupService>();
                services.AddSingleton<ChatService>();
                services.AddSingleton<ConversationManager>();
                services.AddSingleton<EscalationService>();
            })
            .ConfigureLogging((context, logging) =>
            {
                logging.ClearProviders();
                logging.AddConsole();
                logging.AddConfiguration(context.Configuration.GetSection("Logging"));
            });

        return builder.Build();
    }
}
