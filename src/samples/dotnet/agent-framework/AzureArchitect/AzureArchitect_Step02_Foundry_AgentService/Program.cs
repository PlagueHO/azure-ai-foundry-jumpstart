// Copyright (c) Microsoft. All rights reserved.

// This sample shows how to create and use a simple AI agent with Azure Foundry Agents as the backend.

using Azure.AI.Agents.Persistent;
using Azure.Identity;
using Microsoft.Agents.AI;

var endpoint = Environment.GetEnvironmentVariable("AZURE_FOUNDRY_PROJECT_ENDPOINT") ?? throw new InvalidOperationException("AZURE_FOUNDRY_PROJECT_ENDPOINT is not set.");
var deploymentName = Environment.GetEnvironmentVariable("AZURE_FOUNDRY_PROJECT_DEPLOYMENT_NAME") ?? "gpt-4-1";

const string ArchitectName = "AzureArchitect";
const string ArchitectInstructions = """
You are an expert in Azure architecture. You provide direct guidance to help Azure Architects make the best decisions about cloud solutions.
You always review the latest Azure best practices and patterns to ensure your recommendations are:
- up to date
- use the principles of the Azure Well Architected Framework
- keep responses concise and to the point
""";

// Get a client to create/retrieve server side agents with.
var persistentAgentsClient = new PersistentAgentsClient(endpoint, new AzureCliCredential());

// You can create a server side persistent agent with the Azure.AI.Agents.Persistent SDK.
var agentMetadata = await persistentAgentsClient.Administration.CreateAgentAsync(
    model: deploymentName,
    name: ArchitectName + " 1",
    instructions: ArchitectInstructions);

// You can retrieve an already created server side persistent agent as an AIAgent.
AIAgent agent1 = await persistentAgentsClient.GetAIAgentAsync(agentMetadata.Value.Id);

// You can also create a server side persistent agent and return it as an AIAgent directly.
AIAgent agent2 = await persistentAgentsClient.CreateAIAgentAsync(
    model: deploymentName,
    name: ArchitectName + " 2",
    instructions: ArchitectInstructions);

// Create a thread for agent1 to hold the conversation context.
AgentThread thread = agent1.GetNewThread();

Console.WriteLine(await agent1.RunAsync("""
    I am building an AI agent in Azure using Microsoft Agent Framework.
    What Azure services can I use to host it and get 3 9's availability?
    """, thread));

Console.WriteLine("-------------------");

Console.WriteLine(await agent2.RunAsync("""
    I want to use Azure App Service, how do I ensure it is secure?
    """));

// Cleanup for sample purposes.
// await persistentAgentsClient.Administration.DeleteAgentAsync(agent1.Id);
// await persistentAgentsClient.Administration.DeleteAgentAsync(agent2.Id);
