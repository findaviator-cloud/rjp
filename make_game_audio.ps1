# make_game_audio.ps1  (sirf ASCII; Hindi text game_audio_texts.txt se aata hai)
Add-Type -AssemblyName System.Speech
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$out  = Join-Path $here "audio_game"
New-Item -ItemType Directory -Force -Path $out | Out-Null
$s = New-Object System.Speech.Synthesis.SpeechSynthesizer
Write-Host "Installed voices:"
$s.GetInstalledVoices() | ForEach-Object { Write-Host ("  " + $_.VoiceInfo.Name + "  [" + $_.VoiceInfo.Culture.Name + "]") }
$v = $s.GetInstalledVoices() | Where-Object { $_.VoiceInfo.Name -match "Swara" } | Select-Object -First 1
if (-not $v) { $v = $s.GetInstalledVoices() | Where-Object { $_.VoiceInfo.Culture.Name -like "hi*" } | Select-Object -First 1 }
if (-not $v) { Write-Host "ERROR: Hindi voice (Swara) nahi mili. Upar ki list dekhein."; exit 1 }
Write-Host ("Use voice: " + $v.VoiceInfo.Name)
$s.SelectVoice($v.VoiceInfo.Name)
$s.Rate = -2
$ci = New-Object System.Globalization.CultureInfo("hi-IN")
$lines = Get-Content -Encoding UTF8 (Join-Path $here "game_audio_texts.txt")
foreach ($ln in $lines) {
  if ($ln.Trim() -eq "") { continue }
  $p = $ln.Split("|", 2)
  $name = $p[0].Trim(); $text = $p[1].Trim()
  $file = Join-Path $out ($name + ".wav")
  if (Test-Path $file) { Remove-Item $file -Force }
  $s.SetOutputToWaveFile($file)
  $pb = New-Object System.Speech.Synthesis.PromptBuilder($ci)
  $pb.AppendText($text)
  $s.Speak($pb)
  $s.SetOutputToNull()
  $size = (Get-Item $file).Length
  if ($size -lt 5000) { Write-Host ("  FAIL  " + $name + ".wav  " + $size + " bytes (khali)") } else { Write-Host ("  OK    " + $name + ".wav  " + $size + " bytes") }
}
$s.Dispose()
Write-Host "Ho gaya."
