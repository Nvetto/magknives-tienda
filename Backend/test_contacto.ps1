$uri = "https://magknives-backend.onrender.com/contacto"
$headers = @{
    "Content-Type" = "application/json"
}
$body = @{
    nombre = "Test Usuario"
    email = "test@test.com"
    mensaje = "Test desde producción"
} | ConvertTo-Json

Write-Host "🌐 Probando endpoint de contacto en producción..."
Write-Host "📧 Datos: $body"
Write-Host "-" * 50

try {
    $response = Invoke-WebRequest -Uri $uri -Method POST -Headers $headers -Body $body
    Write-Host "✅ Status: $($response.StatusCode)"
    Write-Host "📄 Response: $($response.Content)"
    Write-Host "✅ El endpoint está funcionando correctamente"
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)"
    
    # Intentar obtener más detalles del error
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "🔍 Detalles del error: $responseBody"
    }
}
