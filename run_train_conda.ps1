# Run training with conda tf_gpu environment
$pythonExe = "C:\Users\Admin\.conda\envs\tf_gpu\python.exe"
$scriptPath = "D:\Hoc\Study\computer-vision\DFT-MF\train_cnn_generator.py"

Write-Host "Starting CNN Training (tf_gpu environment)..." -ForegroundColor Cyan

# Add CUDA 11.2 paths (required for TensorFlow 2.10)
$cuda112 = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.2\bin"
if (Test-Path $cuda112) {
    $env:PATH = "$cuda112;$env:PATH"
    Write-Host "Using CUDA 11.2" -ForegroundColor Green
} else {
    Write-Host "WARNING: CUDA 11.2 not found" -ForegroundColor Yellow
}

# Set UTF-8 encoding
$env:PYTHONIOENCODING = "utf-8"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Run training
$startTime = Get-Date
& $pythonExe -u $scriptPath
$exitCode = $LASTEXITCODE
$duration = (Get-Date) - $startTime

Write-Host ""
if ($exitCode -eq 0) {
    Write-Host "[SUCCESS] Training completed in $($duration.ToString('hh\:mm\:ss'))" -ForegroundColor Green
    Write-Host "Check logs: training_logs/" -ForegroundColor Gray
} else {
    Write-Host "[ERROR] Training failed (exit code: $exitCode)" -ForegroundColor Red
}
