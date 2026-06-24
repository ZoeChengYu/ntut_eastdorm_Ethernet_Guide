netsh interface ip set address name="乙太網路" static 140.124.131.120 255.255.255.0 140.124.131.254 
netsh interface ip set dns name="乙太網路" static 140.124.13.1 
netsh interface ip add dns name="乙太網路" 140.124.13.2 index=2
