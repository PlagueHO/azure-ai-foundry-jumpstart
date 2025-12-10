<#
    .SYNOPSIS
        A PowerShell script that combines configuration and deployment of the Microsoft Foundry Jumpstart
        into a single command.

    .DESCRIPTION
        This script automates the process of deploying the Microsoft Foundry Jumpstart. It combines the
        configuration and deployment steps into a single command, making it easier to set up the environment.
        It just makes calls to the Azure Developer CLI command line tool (azd) to do the work.

    .PARAMETER EnvironmentName
        The name of the environment to deploy. If not specified, Azure Developer CLI will prompt the user.

    .PARAMETER EnvironmentVariables
        A hashtable of environment variables to set for the deployment.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [System.String]
    $EnvironmentName,

    [Parameter(Mandatory = $false)]
    [hashtable]
    $EnvironmentVariables
)

foreach ($key in $environmentVariables.Keys) {
    Write-Host "Setting environment variable: $key = $($environmentVariables[$key])"
    azd env set $key $($environmentVariables[$key])
}

if ($Environment) {
    Write-Host "Using environment: $Environment"
    azd up --environment $EnvironmentName
} else {
    azd up
}
