<#
.SYNOPSIS
    Compress each json/txt/yaml sub-folder in the sample-data tree into
    <dataset>.<filetype>.zip located in the dataset root.

.DESCRIPTION
    Iterates over every direct child folder of the supplied root (default:
    ../sample-data). For every sub-folder named json, txt or yaml it collects
    files of the matching extension and creates a ZIP archive
    <dataset>.<filetype>.zip in the dataset folder.

.PARAMETER SampleDataRootPath
    Root folder that contains the dataset folders.

.PARAMETER DeleteSource
    If set, remove the files that were zipped up after a successful archive.

.PARAMETER Force
    Overwrite an existing ZIP file.

.EXAMPLE
    ./compress-sampledata.ps1 -DeleteSource -Verbose -WhatIf
#>
[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'Medium')]
param (
    [System.String]
    $SampleDataRootPath = (Join-Path $PSScriptRoot '..\sample-data'),

    [switch]
    $DeleteSource,

    [switch]
    $Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $SampleDataRootPath)) {
    throw "Sample-data root not found: $SampleDataRootPath"
}

Write-Verbose -Message "Scanning '$SampleDataRootPath' for dataset folders..."

Get-ChildItem -LiteralPath $SampleDataRootPath -Directory | ForEach-Object {
    $datasetDir  = $_.FullName
    $datasetName = $_.Name

    # Gather the sub-folders we want to include
    $subDirs = @('json','yaml','txt').ForEach({
        $d = Join-Path -Path $datasetDir -ChildPath $_
        if (Test-Path -LiteralPath $d) {
            $d
        }
    })

    if ($subDirs.Count -eq 0) {
        return
    }

    $zipPath = Join-Path -Path $datasetDir -ChildPath "$datasetName.zip"

    # Handle existing archive
    if (Test-Path -LiteralPath $zipPath) {
        if (-not $Force) {
            Write-Verbose -Message "Archive exists, skipping: $zipPath"
            return
        }
        elseif ($PSCmdlet.ShouldProcess($zipPath,'Overwrite existing archive')) {
            Remove-Item -LiteralPath $zipPath -Force
        }
    }

    if ($PSCmdlet.ShouldProcess($datasetDir,"Compress -> $zipPath")) {
        Push-Location -LiteralPath $datasetDir
        try {
            Compress-Archive -LiteralPath $subDirs -DestinationPath $zipPath -Force
            Write-Verbose -Message "Created archive: $zipPath"
        } finally {
            Pop-Location
        }

        if ($DeleteSource.IsPresent) {
            Write-Verbose -Message "Deleting original sub-folders for $datasetName"
            $subDirs | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue
        }
    }
}

Write-Verbose -Message 'Compression routine completed.'
