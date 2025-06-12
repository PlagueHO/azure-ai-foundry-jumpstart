#!/usr/bin/env pwsh

# Tech Support Chat Agent - Demo Script
# This script demonstrates the tech support chat agent functionality

Write-Host "🔧 Tech Support Chat Agent - Demo" -ForegroundColor Green
Write-Host "═══════════════════════════════════════" -ForegroundColor Green
Write-Host ""

Write-Host "Building the project..." -ForegroundColor Yellow
$buildResult = dotnet build --verbosity quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Build successful!" -ForegroundColor Green
} else {
    Write-Host "❌ Build failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Testing configuration validation..." -ForegroundColor Yellow
$validateResult = dotnet run -- validate 2>&1
Write-Host "Configuration validation output:"
Write-Host $validateResult -ForegroundColor Cyan

Write-Host ""
Write-Host "Testing agent setup..." -ForegroundColor Yellow
$setupResult = dotnet run -- setup 2>&1
Write-Host "Agent setup output:"
Write-Host $setupResult -ForegroundColor Cyan

Write-Host ""
Write-Host "Available commands:" -ForegroundColor Yellow
Write-Host "  dotnet run -- chat      # Start interactive chat session" -ForegroundColor White
Write-Host "  dotnet run -- validate  # Validate configuration" -ForegroundColor White
Write-Host "  dotnet run -- setup     # Setup Azure AI Agent (placeholder)" -ForegroundColor White
Write-Host "  dotnet run -- --help    # Show help information" -ForegroundColor White

Write-Host ""
Write-Host "Project Features:" -ForegroundColor Yellow
Write-Host "✅ Command-line interface with multiple commands" -ForegroundColor Green
Write-Host "✅ Configuration management via appsettings.json" -ForegroundColor Green
Write-Host "✅ Interactive chat interface with rich console output" -ForegroundColor Green
Write-Host "✅ Conversation management with session tracking" -ForegroundColor Green
Write-Host "✅ Escalation workflows with ticket management" -ForegroundColor Green
Write-Host "✅ Mock responses for demonstration" -ForegroundColor Green
Write-Host "✅ Structured logging with configurable levels" -ForegroundColor Green
Write-Host "✅ Error handling with graceful degradation" -ForegroundColor Green
Write-Host "🚧 Azure AI Agent integration (pending stable SDK)" -ForegroundColor Yellow

Write-Host ""
Write-Host "To test the interactive chat with mock responses:" -ForegroundColor Cyan
Write-Host "  dotnet run -- chat" -ForegroundColor White
Write-Host ""
Write-Host "Sample interaction:" -ForegroundColor Cyan
Write-Host "  You: My computer won't start" -ForegroundColor Gray
Write-Host "  Agent: I understand your problem. Let me suggest some troubleshooting steps..." -ForegroundColor Gray
Write-Host ""
