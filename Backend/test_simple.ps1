$uri = "https://magknives-backend.onrender.com/contacto"
$headers = @{"Content-Type"="application/json"}
$body = '{"nombre":"Test Usuario","email":"test@test.com","mensaje":"Test desde producción"}'

Write-Host "Probando endpoint de contacto..."
$response = Invoke-WebRequest -Uri $uri -Method POST -Headers $headers -Body $body
Write-Host "Status: $($response.StatusCode)"
Write-Host "Response: $($response.Content)"
