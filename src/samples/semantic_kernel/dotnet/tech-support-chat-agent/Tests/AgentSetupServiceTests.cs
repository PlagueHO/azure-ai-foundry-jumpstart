using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;
using TechSupportChatAgent.Configuration;
using TechSupportChatAgent.Services;

namespace TechSupportChatAgent.Tests.Services;

public class AgentSetupServiceTests
{
    private readonly Mock<IConfiguration> _configurationMock;
    private readonly Mock<ILogger<AgentSetupService>> _loggerMock;
    private readonly Mock<IConfigurationSection> _azureAISection;
    private readonly Mock<IConfigurationSection> _agentFrameworkSection;

    public AgentSetupServiceTests()
    {
        _configurationMock = new Mock<IConfiguration>();
        _loggerMock = new Mock<ILogger<AgentSetupService>>();
        _azureAISection = new Mock<IConfigurationSection>();
        _agentFrameworkSection = new Mock<IConfigurationSection>();
        
        _configurationMock.Setup(c => c.GetSection(AzureAIConfiguration.SectionName))
            .Returns(_azureAISection.Object);
        _configurationMock.Setup(c => c.GetSection(AgentFrameworkConfiguration.SectionName))
            .Returns(_agentFrameworkSection.Object);
    }

    [Fact]
    public void Constructor_ShouldInitializeWithValidConfiguration()
    {
        // Arrange
        SetupValidConfiguration();
        
        // Act
        var service = new AgentSetupService(_configurationMock.Object, _loggerMock.Object);
        
        // Assert
        Assert.NotNull(service);
    }

    [Fact]
    public void ValidateConfiguration_WithValidConfig_ShouldReturnTrue()
    {
        // Arrange
        SetupValidConfiguration();
        var service = new AgentSetupService(_configurationMock.Object, _loggerMock.Object);
        
        // Act
        var result = service.ValidateConfiguration();
        
        // Assert
        Assert.True(result);
    }

    [Fact]
    public void ValidateConfiguration_WithInvalidConfig_ShouldReturnFalse()
    {
        // Arrange
        SetupInvalidConfiguration();
        var service = new AgentSetupService(_configurationMock.Object, _loggerMock.Object);
        
        // Act
        var result = service.ValidateConfiguration();
        
        // Assert
        Assert.False(result);
    }

    [Fact]
    public async Task CreateAgentAsync_ShouldReturnNull_WhenNotYetImplemented()
    {
        // Arrange
        SetupValidConfiguration();
        var service = new AgentSetupService(_configurationMock.Object, _loggerMock.Object);
        
        // Act
        var result = await service.CreateAgentAsync();
        
        // Assert
        Assert.Null(result);
    }

    [Fact]
    public void GetAzureAIConfiguration_ShouldReturnConfiguration()
    {
        // Arrange
        SetupValidConfiguration();
        var service = new AgentSetupService(_configurationMock.Object, _loggerMock.Object);
        
        // Act
        var config = service.GetAzureAIConfiguration();
        
        // Assert
        Assert.NotNull(config);
        Assert.Equal("https://test.endpoint.com", config.FoundryEndpoint);
        Assert.Equal("gpt-4o", config.ModelName);
    }

    [Fact]
    public void GetAgentFrameworkConfiguration_ShouldReturnConfiguration()
    {
        // Arrange
        SetupValidConfiguration();
        var service = new AgentSetupService(_configurationMock.Object, _loggerMock.Object);
        
        // Act
        var config = service.GetAgentFrameworkConfiguration();
        
        // Assert
        Assert.NotNull(config);
        Assert.Equal("TechSupportAgent", config.AgentName);
        Assert.Equal(50, config.MaxConversationTurns);
        Assert.Equal(3, config.EscalationThreshold);
    }

    private void SetupValidConfiguration()
    {
        var azureConfig = new AzureAIConfiguration
        {
            FoundryEndpoint = "https://test.endpoint.com",
            ModelName = "gpt-4o",
            ProjectName = "test-project",
            TenantId = "test-tenant",
            ClientId = "test-client"
        };

        var agentConfig = new AgentFrameworkConfiguration
        {
            AgentName = "TechSupportAgent",
            AgentDescription = "Test description",
            Instructions = "Test instructions",
            MaxConversationTurns = 50,
            EscalationThreshold = 3,
            VectorStoreId = "test-vector-store",
            KnowledgeBaseFiles = new List<string> { "file1", "file2" }
        };

        MockConfigurationBinding(_azureAISection, azureConfig);
        MockConfigurationBinding(_agentFrameworkSection, agentConfig);
    }

    private void SetupInvalidConfiguration()
    {
        var azureConfig = new AzureAIConfiguration
        {
            FoundryEndpoint = "", // Invalid - empty
            ModelName = "",       // Invalid - empty
            ProjectName = "test-project",
            TenantId = "test-tenant",
            ClientId = "test-client"
        };

        var agentConfig = new AgentFrameworkConfiguration
        {
            AgentName = "",      // Invalid - empty
            Instructions = "",   // Invalid - empty
            MaxConversationTurns = -1,  // Invalid - negative
            EscalationThreshold = 0     // Invalid - zero
        };

        MockConfigurationBinding(_azureAISection, azureConfig);
        MockConfigurationBinding(_agentFrameworkSection, agentConfig);
    }

    private void MockConfigurationBinding<T>(Mock<IConfigurationSection> sectionMock, T configObject)
        where T : class
    {
        sectionMock.Setup(s => s.Bind(It.IsAny<T>()))
            .Callback<T>(target =>
            {
                var properties = typeof(T).GetProperties();
                foreach (var prop in properties)
                {
                    var value = prop.GetValue(configObject);
                    prop.SetValue(target, value);
                }
            });
    }
}
