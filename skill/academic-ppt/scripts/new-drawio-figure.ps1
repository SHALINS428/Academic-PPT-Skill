param(
    [Parameter(Mandatory = $true)]
    [string]$OutputPath,

    [string]$Title = 'Academic Diagram',
    [string]$PageName = 'Page-1',
    [int]$Width = 1920,
    [int]$Height = 1080
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$outputDir = Split-Path -Parent $OutputPath
if ($outputDir -and -not (Test-Path -LiteralPath $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

$diagramId = [guid]::NewGuid().ToString('N').Substring(0, 12)
$modified = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')

$xml = @"
<mxfile host="app.diagrams.net" modified="$modified" agent="Codex Drawio Skill" version="24.7.17" type="device">
  <diagram id="$diagramId" name="$PageName">
    <mxGraphModel dx="$Width" dy="$Height" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="$Width" pageHeight="$Height" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <mxCell id="title" value="$Title" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=24;fontStyle=1;fontFamily=Arial;fontColor=#1F2937;" vertex="1" parent="1">
          <mxGeometry x="48" y="24" width="680" height="40" as="geometry" />
        </mxCell>
        <mxCell id="note" value="Edit this starter file in diagrams.net. Deliver both the final .drawio source and a matching PNG. Clean up routing, spacing, and typography before considering the figure complete." style="rounded=1;whiteSpace=wrap;html=1;fillColor=#F8FAFC;strokeColor=#CBD5E1;fontSize=16;fontFamily=Arial;fontColor=#334155;spacing=12;" vertex="1" parent="1">
          <mxGeometry x="48" y="84" width="760" height="120" as="geometry" />
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
"@

[System.IO.File]::WriteAllText($OutputPath, $xml, (New-Object System.Text.UTF8Encoding($false)))
Write-Output $OutputPath
