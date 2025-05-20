import os
import subprocess

# 1. Write hostapd config
hostapd_conf = """
interface=wlan0
driver=nl80211
ssid=Pi_AP
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=raspberry
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP
"""
with open("/etc/hostapd/hostapd.conf", "w") as f:
    f.write(hostapd_conf)

# 2. Write dnsmasq config
dnsmasq_conf = """
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
"""
with open("/etc/dnsmasq.conf", "w") as f:
    f.write(dnsmasq_conf)

# 3. Configure static IP for wlan0
os.system("sudo ifconfig wlan0 192.168.4.1 netmask 255.255.255.0")

# 4. Enable IP forwarding
with open("/proc/sys/net/ipv4/ip_forward", "w") as f:
    f.write("1")

# 5. Set up NAT (masquerading)
os.system("sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE")
os.system("sudo iptables -A FORWARD -i eth0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT")
os.system("sudo iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT")

# 6. Start services
subprocess.call(["sudo", "systemctl", "restart", "hostapd"])
subprocess.call(["sudo", "systemctl", "restart", "dnsmasq"])

print("Access point with internet sharing is set up!")