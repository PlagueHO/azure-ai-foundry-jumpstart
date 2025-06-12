using Microsoft.Extensions.Configuration;

namespace TechSupportChatAgent.Configuration;

/// <summary>
/// Configuration settings for Azure AI Foundry integration.
/// </summary>
public class AzureAIConfiguration
{
    public const string SectionName = "AzureAI";
    
    /// <summary>
    /// Azure AI Foundry project endpoint URL.
    /// </summary>
    public string FoundryEndpoint { get; set; } = string.Empty;
    
    /// <summary>
    /// Azure AI Foundry project name.
    /// </summary>
    public string ProjectName { get; set; } = string.Empty;
    
    /// <summary>
    /// AI model name to use (e.g., "gpt-4o").
    /// </summary>
    public string ModelName { get; set; } = string.Empty;
    
    /// <summary>
    /// Azure AD tenant ID for authentication.
    /// </summary>
    public string TenantId { get; set; } = string.Empty;
    
    /// <summary>
    /// Azure AD client ID for authentication.
    /// </summary>
    public string ClientId { get; set; } = string.Empty;
    
    /// <summary>
    /// Validates the configuration settings.
    /// </summary>
    public void Validate()
    {
        if (string.IsNullOrWhiteSpace(FoundryEndpoint))
            throw new InvalidOperationException("AzureAI:FoundryEndpoint is required");
            
        if (string.IsNullOrWhiteSpace(ModelName))
            throw new InvalidOperationException("AzureAI:ModelName is required");
            
        if (!Uri.TryCreate(FoundryEndpoint, UriKind.Absolute, out _))
            throw new InvalidOperationException("AzureAI:FoundryEndpoint must be a valid URL");
    }
}

/// <summary>
/// Configuration settings for the Agent Framework.
/// </summary>
public class AgentFrameworkConfiguration
{
    public const string SectionName = "AgentFramework";
    
    /// <summary>
    /// Name of the agent.
    /// </summary>
    public string AgentName { get; set; } = "TechSupportAgent";
    
    /// <summary>
    /// Description of the agent's purpose.
    /// </summary>
    public string AgentDescription { get; set; } = "Technical support agent for troubleshooting and assistance";
    
    /// <summary>
    /// Maximum number of conversation turns before offering escalation.
    /// </summary>
    public int MaxConversationTurns { get; set; } = 50;
    
    /// <summary>
    /// Number of failed attempts before triggering escalation workflow.
    /// </summary>
    public int EscalationThreshold { get; set; } = 3;
    
    /// <summary>
    /// Agent instructions template.
    /// </summary>
    public string Instructions { get; set; } = string.Empty;
    
    /// <summary>
    /// Azure AI Foundry vector store ID for knowledge base.
    /// </summary>
    public string VectorStoreId { get; set; } = string.Empty;
    
    /// <summary>
    /// List of knowledge base file IDs.
    /// </summary>
    public List<string> KnowledgeBaseFiles { get; set; } = new();
    
    /// <summary>
    /// Validates the configuration settings.
    /// </summary>
    public void Validate()
    {
        if (string.IsNullOrWhiteSpace(AgentName))
            throw new InvalidOperationException("AgentFramework:AgentName is required");
            
        if (string.IsNullOrWhiteSpace(Instructions))
            throw new InvalidOperationException("AgentFramework:Instructions is required");
            
        if (MaxConversationTurns <= 0)
            throw new InvalidOperationException("AgentFramework:MaxConversationTurns must be greater than 0");
            
        if (EscalationThreshold <= 0)
            throw new InvalidOperationException("AgentFramework:EscalationThreshold must be greater than 0");
    }
}
