param($FilePath)

$videoExtensions = @('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg')
$extension = [System.IO.Path]::GetExtension($FilePath).ToLower()

if ($videoExtensions -contains $extension) {
    python "d:\Github\RecodeCLI\recode.py" $FilePath --t "D:\Movies" --abr 256k --c hevc_qsv
}