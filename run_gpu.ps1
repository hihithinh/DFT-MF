# Run crop_open_mouth_gpu.py with proper Python from venv
$pythonExe = "D:\Hoc\Study\computer-vision\DFT-MF\venv_windows\Scripts\python.exe"
$scriptPath = "D:\Hoc\Study\computer-vision\DFT-MF\crop_open_mouth_gpu.py"

Write-Host "Starting GPU-accelerated face detection..." -ForegroundColor Cyan
Write-Host "Python: $pythonExe" -ForegroundColor Gray
Write-Host "Script: $scriptPath" -ForegroundColor Gray
Write-Host ""

# Verify dlib CUDA
Write-Host "Verifying GPU support..." -ForegroundColor Yellow
& $pythonExe -c "import dlib; print('dlib CUDA:', dlib.DLIB_USE_CUDA)"
Write-Host ""

# Add CUDA and cuDNN to PATH for DLL loading
$cudaPath = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.2\bin"
$cudnnPath = "C:\Program Files\NVIDIA\CUDNN\v9.20\bin\13.2\x64"

if (Test-Path $cudaPath) {
    $env:PATH = "$cudaPath;$env:PATH"
    Write-Host "Added CUDA to PATH: $cudaPath" -ForegroundColor Gray
}

if (Test-Path $cudnnPath) {
    $env:PATH = "$cudnnPath;$env:PATH"
    Write-Host "Added cuDNN to PATH: $cudnnPath" -ForegroundColor Gray
} else {
    Write-Host "WARNING: cuDNN path not found: $cudnnPath" -ForegroundColor Yellow
}

Write-Host ""

# Run the script
Write-Host "Running script..." -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Gray

try {
    & $pythonExe -u $scriptPath 2>&1 | ForEach-Object {
        Write-Host $_
    }
    $exitCode = $LASTEXITCODE
} catch {
    Write-Host "ERROR: $_" -ForegroundColor Red
    $exitCode = 1
}

Write-Host "============================================================" -ForegroundColor Gray
Write-Host ""

if ($exitCode -eq 0) {
    Write-Host "Script finished successfully!" -ForegroundColor Green
} else {
    Write-Host "Script finished with errors (exit code: $exitCode)" -ForegroundColor Red
}
