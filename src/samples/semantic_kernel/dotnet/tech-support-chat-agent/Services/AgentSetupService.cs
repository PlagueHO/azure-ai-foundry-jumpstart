using Microsoft.SemanticKernel.Agents.AzureAI;
using Azure;
using Azure.Identity;
using Azure.AI.Projects;
using Azure.AI.Agents.Persistent;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Microsoft.SemanticKernel;
using TechSupportChatAgent.Configuration;
using TechSupportChatAgent.Models;

#pragma warning disable SKEXP0001 // Type is for evaluation purposes only
#pragma warning disable SKEXP0110 // Type is for evaluation purposes only

namespace TechSupportChatAgent.Services;

/// <summary>
/// Service for setting up and configuring Azure AI Agents.
/// </summary>
public class AgentSetupService
{
    private readonly IConfiguration _configuration;
    private readonly ILogger<AgentSetupService> _logger;
    private readonly AzureAIConfiguration _azureConfig;
    private readonly AgentFrameworkConfiguration _agentConfig;

    public AgentSetupService(
        IConfiguration configuration,
        ILogger<AgentSetupService> logger)
    {
        _configuration = configuration;
        _logger = logger;
        
        _azureConfig = new AzureAIConfiguration();
        _configuration.GetSection(AzureAIConfiguration.SectionName).Bind(_azureConfig);
        _azureConfig.Validate();
        
        _agentConfig = new AgentFrameworkConfiguration();
        _configuration.GetSection(AgentFrameworkConfiguration.SectionName).Bind(_agentConfig);
        _agentConfig.Validate();
    }    /// <summary>
    /// Creates and configures an Azure AI Agent with file search capabilities.
    /// </summary>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Configured Azure AI Agent.</returns>
    public async Task<AzureAIAgent?> CreateAgentAsync(CancellationToken cancellationToken = default)
    {
        try
        {
            _logger.LogInformation("Setting up Azure AI Agent for tech support");
            
            // Create the AIProjectClient using the GA approach
            var endpoint = new Uri(_azureConfig.FoundryEndpoint);
            var credential = new DefaultAzureCredential();
            var projectClient = new AIProjectClient(endpoint, credential);
            
            // Get the PersistentAgentsClient from the project client
            var agentsClient = projectClient.GetPersistentAgentsClient();
            
            _logger.LogInformation("Created AIProjectClient and PersistentAgentsClient for endpoint: {Endpoint}", _azureConfig.FoundryEndpoint);
            
            // Create the agent definition using the GA API pattern
            PersistentAgent definition;
            
            if (!string.IsNullOrEmpty(_agentConfig.VectorStoreId))
            {
                // Create agent with File Search tool and vector store
                definition = await agentsClient.Administration.CreateAgentAsync(
                    model: _azureConfig.ModelName,
                    name: _agentConfig.AgentName,
                    description: _agentConfig.AgentDescription,
                    instructions: _agentConfig.Instructions,
                    tools: [new FileSearchToolDefinition()],
                    toolResources: new()
                    {
                        FileSearch = new()
                        {
                            VectorStoreIds = { _agentConfig.VectorStoreId }
                        }
                    },
                    cancellationToken: cancellationToken);
                    
                _logger.LogInformation("Created agent with File Search and vector store: {VectorStoreId}", _agentConfig.VectorStoreId);
            }
            else
            {
                // Create basic agent with File Search tool (no specific vector store)
                definition = await agentsClient.Administration.CreateAgentAsync(
                    model: _azureConfig.ModelName,
                    name: _agentConfig.AgentName,
                    description: _agentConfig.AgentDescription,
                    instructions: _agentConfig.Instructions,
                    tools: [new FileSearchToolDefinition()],
                    cancellationToken: cancellationToken);
                    
                _logger.LogInformation("Created agent with File Search tool (no specific vector store)");
            }
                
            _logger.LogInformation("Created agent definition with ID: {AgentId}", definition.Id);
            
            // Create the Semantic Kernel AzureAIAgent wrapper
            var agent = new AzureAIAgent(definition, agentsClient);
            
            _logger.LogInformation("Successfully created Azure AI Agent for tech support");
            
            return agent;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to create Azure AI Agent");
            throw;
        }
    }

    /// <summary>
    /// Validates the current configuration for agent setup.
    /// </summary>
    /// <returns>True if configuration is valid.</returns>
    public bool ValidateConfiguration()
    {
        try
        {
            _azureConfig.Validate();
            _agentConfig.Validate();
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Configuration validation failed");
            return false;
        }
    }

    /// <summary>
    /// Gets the current Azure AI configuration.
    /// </summary>
    public AzureAIConfiguration GetAzureAIConfiguration() => _azureConfig;

    /// <summary>
    /// Gets the current agent framework configuration.
    /// </summary>
    public AgentFrameworkConfiguration GetAgentFrameworkConfiguration() => _agentConfig;
}
