# Navigate to the project package directory
Set-Location "C:\{path}\{to}\{project}\{project}"

# Check if the .venv folder exists
if (Test-Path ".venv") {
    # Activate the virtual environment
    & ".venv\Scripts\Activate.ps1"

    # Run the main Python script
    python "{project}\main.py"

    # Deactivate the virtual environment
    deactivate
} else {
    # If .venv does not exist, just run the main Python script without activation
    python "{project}\main.py"
}
