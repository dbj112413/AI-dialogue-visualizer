#【Activate .venv】
# 1. Navigate to new project
''' type this first '''
# cd "C:\Users\C\OneDrive\Desktop\計算機程式設計\code\114-1\AI-dialogue-project"

# 2. Activate the copied .venv
.\.venv\Scripts\Activate.ps1

# 3. Verify activation (you should see (.venv) in prompt)
# (.venv) PS C:\...\AI-dialogue-project>

#【Verify current .venv】
# After activating
.\.venv\Scripts\Activate.ps1

# Check which Python executable is being used
Get-Command python | Select-Object Source

# Output should show:
# Source
# ------
# C:\Users\C\OneDrive\Desktop\計算機程式設計\code\114-1\AI-dialogue-project\.venv\Scripts\python.exe
#                                                              ^^^^^^^^^^^^^^^^^^^
#                                                              NEW project folder!