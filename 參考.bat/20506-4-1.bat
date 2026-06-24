@echo off
:: 確保指令路徑正確，避免環境變數問題
SET CMD_NETSH=C:\Windows\System32\netsh.exe

echo [1/3] 正在設定靜態 IP (140.124.131.120)...
%CMD_NETSH% interface ip set address name="乙太網路" static 140.124.131.120 255.255.255.0 140.124.131.254

echo [2/3] 正在設定主要 DNS (140.124.13.1)...
%CMD_NETSH% interface ip set dns name="乙太網路" static 140.124.13.1

echo [3/3] 正在設定次要 DNS (140.124.13.2)...
%CMD_NETSH% interface ip add dns name="乙太網路" 140.124.13.2 index=2

echo.
echo 設定完成！檢查結果：
%CMD_NETSH% interface ip show config name="乙太網路"

pause