function Test-Function {
    try {
        Write-Host "Test - OK"
    }
    catch {
        Write-Host "Test - Error"
    }
}

Test-Function
Write-Host "Done"