param(
    [string]$TorrentName,
    [string]$ContentPath,
    [string]$RootPath,
    [string]$SavePath,
    [string]$Category,
    [string]$Tags,
    [int]$FileCount
)

$logFile = "D:\Downloads\qbittorrent-recode.log"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# Log the trigger
Add-Content -Path $logFile -Value "[$timestamp] ===== Script triggered ====="
Add-Content -Path $logFile -Value "TorrentName: $TorrentName"
Add-Content -Path $logFile -Value "ContentPath: $ContentPath"
Add-Content -Path $logFile -Value "RootPath: $RootPath"
Add-Content -Path $logFile -Value "SavePath: $SavePath"
Add-Content -Path $logFile -Value "Category: $Category"
Add-Content -Path $logFile -Value "Tags: $Tags"
Add-Content -Path $logFile -Value "FileCount: $FileCount"

$videoExtensions = @('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg', '.ts', '.m2ts')

function Process-VideoFile {
    param([string]$FilePath)
    
    $extension = [System.IO.Path]::GetExtension($FilePath).ToLower()
    
    if ($videoExtensions -contains $extension) {
        Add-Content -Path $logFile -Value "Processing video: $FilePath"
        
        try {
            $output = python "d:\Github\RecodeCLI\recode.py" $FilePath --t "D:\Movies" --abr 256k --c hevc_qsv 2>&1
            Add-Content -Path $logFile -Value "Success: $output"
        } catch {
            Add-Content -Path $logFile -Value "Error: $_"
        }
    } else {
        Add-Content -Path $logFile -Value "Skipping non-video: $FilePath"
    }
}

# Check if ContentPath is a file or directory
if (Test-Path -Path $ContentPath -PathType Leaf) {
    # Single file torrent
    Process-VideoFile -FilePath $ContentPath
} elseif (Test-Path -Path $ContentPath -PathType Container) {
    # Multi-file torrent - find all video files
    Add-Content -Path $logFile -Value "Scanning directory for videos..."
    Get-ChildItem -Path $ContentPath -Recurse -File | ForEach-Object {
        Process-VideoFile -FilePath $_.FullName
    }
} else {
    Add-Content -Path $logFile -Value "ERROR: Path not found: $ContentPath"
}

Add-Content -Path $logFile -Value "[$timestamp] ===== Script finished =====`n"
