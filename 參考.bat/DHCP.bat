@echo off
chcp 65001
:: 確保指令路徑正確，避免環境變數問題
SET CMD_NETSH=C:\Windows\System32\netsh.exe
echo [1/2] 正在設定動態 IP ...
netsh interface ip set address name="乙太網路" source=dhcp
echo [2/2] 正在設定動態取得 DNS ...
netsh interface ip set dns name="乙太網路" source=dhcp
echo 已恢復為自動取得 IP。
echo.
echo 設定完成！檢查結果：
%CMD_NETSH% interface ip show config name="乙太網路"
pause