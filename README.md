# 北科大宿舍有線網路攻略(ntut_eastdorm_Ethernet_Guide)

## 第零章	前置作業

在你連上優質又穩定的宿網之前，你必須確認你準備的電腦是否有 RJ45 網孔（如下[圖 1](./圖檔/圖片1.jpg)）以及網路線（如下[圖 2](./圖檔/圖片2.jpg)，若是桌上型電腦 PC，建議網路線長度超過 3m）。若電腦沒有 RJ45 網孔，請先購買 USB-C / Type-C 轉 RJ45 網路轉接頭；若沒有網路線，請先購買網路線（建議購買 Cat5e 或 Cat6 等規格的網路線以支援 Giga 級網速）。

| [![圖1](./圖檔/圖片1.jpg)](./圖檔/圖片1.jpg) | [![圖2](./圖檔/圖片2.jpg)](./圖檔/圖片2.jpg) |
| :--: | :--: |
| 圖 1 | 圖 2 |

## 第壹章	網際網路設定

### 方法一：使用圖形化介面 (GUI)

#### 步驟 1 ：先開啟 Windows「設定」

[![圖3](./圖檔/圖片3.png)](./圖檔/圖片3.png)

#### 步驟 2 ：點選「網路與網際網路」，接著點選「乙太網路」

[![圖4](./圖檔/圖片4.png)](./圖檔/圖片4.png)

#### 步驟 3 ：在「IP 指派」點選「編輯」

[![圖5](./圖檔/圖片5.png)](./圖檔/圖片5.png)

#### 步驟 4 ：將「編輯 IP 設定」從「自動 (DHCP)」切換為「手動」

[![圖6](./圖檔/圖片6.png)](./圖檔/圖片6.png)

#### 步驟 5 ：開啟「IPv4」選項，「IPv6」請保持關閉

#### 步驟 6 ：依照宿網設定填寫 IP 位址、子網路遮罩、閘道與 DNS，並按儲存

[![圖7](./圖檔/圖片7.png)](./圖檔/圖片7.png)

### 方法二：Windows 系統 — 使用命令提示字元 (CMD) 【使用 .bat 檔自動設定】

#### 步驟 1 ：將指令複製到記事本

##### 第一種打法

``` shell showLineNumbers
netsh interface ip set address name="乙太網路" static {你的IP位址} 255.255.255.0 {你的IP位址的末碼改成254} 
netsh interface ip set dns name="乙太網路" static 140.124.13.1 
netsh interface ip add dns name="乙太網路" 140.124.13.2 index=2
```

假設IP位址為140.124.131.120則我需要這樣打

``` shell showLineNumbers
netsh interface ip set address name="乙太網路" static 140.124.131.120 255.255.255.0 140.124.131.254 
netsh interface ip set dns name="乙太網路" static 140.124.13.1 
netsh interface ip add dns name="乙太網路" 140.124.13.2 index=2
```

##### 第二種打法(推薦)

``` shell showLineNumbers
@echo off
:: 確保指令路徑正確，避免環境變數問題
SET CMD_NETSH=C:\Windows\System32\netsh.exe
echo [1/3] 正在設定靜態 IP ...
%CMD_NETSH% interface ip set address name="乙太網路" static {你的IP位址} 255.255.255.0 {你的IP位址的末碼改成254}
echo [2/3] 正在設定主要 DNS ...
%CMD_NETSH% interface ip set dns name="乙太網路" static 140.124.13.1
echo [3/3] 正在設定次要 DNS ...
%CMD_NETSH% interface ip add dns name="乙太網路" 140.124.13.2 index=2
echo.
echo 設定完成！檢查結果：
%CMD_NETSH% interface ip show config name="乙太網路"
pause
```

假設IP位址為140.124.131.120則我需要這樣打

``` shell showLineNumbers
@echo off
:: 確保指令路徑正確，避免環境變數問題
SET CMD_NETSH=C:\Windows\System32\netsh.exe
echo [1/3] 正在設定靜態 IP ...
%CMD_NETSH% interface ip set address name="乙太網路" static 140.124.131.120 255.255.255.0 140.124.131.254
echo [2/3] 正在設定主要 DNS ...
%CMD_NETSH% interface ip set dns name="乙太網路" static 140.124.13.1
echo [3/3] 正在設定次要 DNS ...
%CMD_NETSH% interface ip add dns name="乙太網路" 140.124.13.2 index=2
echo.
echo 設定完成！檢查結果：
%CMD_NETSH% interface ip show config name="乙太網路"
pause
```

##### 附錄：使用DHCP(動態分配IP)打法【宿舍不能用】

>
>只有這個使用UTF-8也沒問題
>

``` shell showLineNumbers
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
```

#### 步驟 2 ：以 ANSI 編碼方式儲存檔案

[![圖8](./圖檔/圖片8.png)](./圖檔/圖片8.png)

#### 步驟 3 ：將副檔名從 .txt 改成 .bat

[![圖9](./圖檔/圖片9.png)](./圖檔/圖片9.png) | [![圖10](./圖檔/圖片10.png)](./圖檔/圖片10.png) | [![圖11](./圖檔/圖片11.png)](./圖檔/圖片11.png) |
| :--: | :--: | :--: |
| 圖 9 | 圖 10 |  圖 11 |

#### 步驟 4 ：以系統管理員身分執行該檔案

[![圖12](./圖檔/圖片12.png)](./圖檔/圖片12.png)

#### 步驟 5 ：看到 CMD 視窗顯示設定完成即完成設定

[![圖13](./圖檔/圖片13.png)](./圖檔/圖片13.png)

---

### 方法三：Linux / macOS 系統 — 使用終端機 (Terminal) 【直接執行指令】

#### Linux 系統 (使用 nmcli)

多數現代 Linux 發行版 (如 Ubuntu, Debian, Fedora, Arch) 皆預設使用 NetworkManager，因此推薦使用 `nmcli` 命令列工具。

1. **查詢網路卡連線名稱**：
   ```shell
   nmcli connection show
   ```
   請記下你要設定的有線網路連線名稱（中文系統通常為 `有線連線 1`，英文系統為 `Wired connection 1`，以下以 `"有線連線 1"` 為例）。

2. **設定靜態 IP、閘道與 DNS**：
   ```shell
   # 設定 IP 位址與子網路遮罩 (請將 {你的IP位址} 替換成實際分配的 IP)
   sudo nmcli connection modify "有線連線 1" ipv4.addresses {你的IP位址}/24
   
   # 設定預設閘道 (Gateway) (例如將 IP 位址的最後一碼改成 254)
   sudo nmcli connection modify "有線連線 1" ipv4.gateway {你的IP位址的末碼改成254}
   
   # 設定主要與次要 DNS 伺服器
   sudo nmcli connection modify "有線連線 1" ipv4.dns "140.124.13.1 140.124.13.2"
   
   # 設定為手動 (靜態) 模式
   sudo nmcli connection modify "有線連線 1" ipv4.method manual
   ```

   例如IP位址為140.124.131.120則我需要這樣打
   
   ```shell
   sudo nmcli connection modify "有線連線 1" ipv4.addresses 140.124.131.120/24
   sudo nmcli connection modify "有線連線 1" ipv4.gateway 140.124.131.254
   sudo nmcli connection modify "有線連線 1" ipv4.dns "140.124.13.1 140.124.13.2"
   sudo nmcli connection modify "有線連線 1" ipv4.method manual
   ```

3. **重新啟動網路連線以套用設定**：
   ```shell
   sudo nmcli connection down "有線連線 1"
   sudo nmcli connection up "有線連線 1"
   ```

4. **恢復自動取得 IP (DHCP) [宿舍有線網路不能用]**：
   ```shell
   sudo nmcli connection modify "有線連線 1" ipv4.method auto
   sudo nmcli connection up "有線連線 1"
   ```

#### macOS 系統 (使用 networksetup)

macOS 系統可以使用內建的 `networksetup` 指令進行設定。

1. **查詢網路服務名稱**：
   ```shell
   networksetup -listallnetworkservices
   ```
   請記下你的有線網路服務名稱 (通常為 `Ethernet` 或 `AX88179A` 等外接轉接卡名稱，以下以 `"Ethernet"` 為例)。

2. **設定靜態 IP、子網路遮罩與閘道**：
   ```shell
   sudo networksetup -setmanual "Ethernet" {你的IP位址} 255.255.255.0 {你的IP位址的末碼改成254}
   ```

3. **設定主要與次要 DNS**：
   ```shell
   sudo networksetup -setdnsservers "Ethernet" 140.124.13.1 140.124.13.2
   ```

4. **恢復自動取得 IP (DHCP) [宿舍有線網路不能用]**：
   ```shell
   sudo networksetup -setdhcp "Ethernet"
   ```

## 第貳章	登錄裝置與連結IP

#### 步驟1 ：首先，請先登錄校園入口網站

#### 步驟2 ：點擊「網路管理」，接著點擊網路與資訊安全管理系統

[![圖14](./圖檔/圖片14.png)](./圖檔/圖片14.png)

#### 步驟3 ：完成點擊之後，自動新開分頁「網路與資訊安全管理系統」

#### 步驟4 ：點擊「IP與MAC」，接著點擊「設備(MAC)管理」

[![圖15](./圖檔/圖片15.png)](./圖檔/圖片15.png)

#### 步驟5 ：點擊「新增」

[![圖16](./圖檔/圖片16.png)](./圖檔/圖片16.png)

> [!TIP]
> **如何取得網路卡實體位址 (MAC Address)？**
>
> **Windows 系統：**
> 1. **使用圖形化介面 (GUI)**：回到「方法一：使用圖形化介面 (GUI)」的乙太網路設定頁面，在下方會看到「實體位址 (MAC)」，將其複製即可。
>    [![圖17](./圖檔/圖片17.png)](./圖檔/圖片17.png)
> 2. **使用命令提示字元 (CMD)**：輸入 `getmac /v /fo list` 指令，找到有線網路卡（例如「乙太網路」或「Ethernet」）對應的「實體位址」即可。
>    ```shell
>    getmac /v /fo list
>    ```
>    [![圖18](./圖檔/圖片18.png)](./圖檔/圖片18.png)
>
> **Linux 系統：**
> 1. **使用終端機**：開啟終端機輸入 `ip link show` 指令，找到有線網卡（通常以 `en` 或 `eth` 開頭）下方的 `link/ether`，後面的 12 碼十六進位字元即為 MAC 位址。
>    ```shell
>    ip link show
>    ```
>
> **macOS 系統：**
> 1. **使用圖形化介面**：點擊左上角「蘋果選單」  >「系統設定」>「網路」> 點擊你的有線網路服務（如「USB 10/100/1000 LAN」）> 點擊「詳細資訊...」> 點擊左側「硬體」，即可看到「MAC 位址」。
> 2. **使用終端機**：開啟 Terminal 輸入下述指令即可顯示硬體連接埠與其對應的 MAC 位址（請找 `Ethernet` 或對應外接轉接卡的 `Ethernet Address`）：
>    ```shell
>    networksetup -listallhardwareports
>    ```

#### 步驟6 ：依照真實情況去做填寫

[![圖19](./圖檔/圖片19.png)](./圖檔/圖片19.png)

#### 步驟7 ：完成後，點擊「IP與MAC」，接著點擊「設備(MAC)管理」

#### 步驟8 ：接著點擊連結符號連結裝置

[![圖20](./圖檔/圖片20.png)](./圖檔/圖片20.png)

## 第參章 相關連結

### 網路組連結

[![網路組連結](./圖檔/圖片21.png)](https://line.me/R/ti/p/@222dnqse)

### 電力系統
|  | ![電力首頁](./圖檔/圖片22.png) | ![客服中心](./圖檔/圖片23.png) | ![啟用電力](./圖檔/圖片24.png) |
| :-: | :-: | :-: | :-: |
| [簡報](北科-智慧電力計費管理系統網頁平台操作手冊（學生）.pdf) | [首頁](https://www.aotech.tw/ntut) | [客服中心](https://www.aotech.tw/ntut/content_us.php) | [啟用電力](https://www.aotech.tw/ntut_power) |