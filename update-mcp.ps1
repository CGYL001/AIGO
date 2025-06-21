try {
    $mcp_config = Get-Content -Raw C:\Users\14179\.cursor\mcp.json | ConvertFrom-Json
    if ($mcp_config.mcpServers.PSObject.Properties.Name -contains "AIgo-model-manager") {
        Write-Host "AIgo服务器配置已存在，将更新配置"
        $mcp_config.mcpServers."AIgo-model-manager" = @{
            command = "python"
            args = @("D:/AIgo/http_server.py")
            timeout = 300
            autoApprove = @("model_switch", "model_optimize")
        }
    } else {
        Write-Host "添加AIgo服务器配置"
        $mcp_config.mcpServers | Add-Member -Name "AIgo-model-manager" -Value @{
            command = "python"
            args = @("D:/AIgo/http_server.py")
            timeout = 300
            autoApprove = @("model_switch", "model_optimize")
        } -MemberType NoteProperty
    }
    $mcp_config | ConvertTo-Json -Depth 10 | Out-File -FilePath C:\Users\14179\.cursor\mcp.json -Encoding utf8
    Write-Host "配置已成功保存"
} catch {
    Write-Host "错误: $_"
} 