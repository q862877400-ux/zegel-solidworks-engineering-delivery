import sys
sys.stdout.reconfigure(encoding="utf-8")
import requests
APP = "77f56fb2-4165-4116-b82f-e495838bb6e1"
U = "https://api.cn.misumi.com.cn/api/v1/type/search"
H = {"User-Agent": "Mozilla/5.0 Chrome/131.0", "Referer": "https://www.misumi.com.cn/"}
print("  核 ①：applicationId 放 header（不带走 query）")
r = requests.get(U, params={"partNumber": "HFS5-4040"}, headers=dict(H, applicationId=APP), timeout=20)
print("     -> %d  %s" % (r.status_code, (r.status_code == 200 and "200-OK" or (r.json().get("errorList") or [{}])[0].get("errorCode", "?"))))
print("  核 ②：完全不带 applicationId")
r = requests.get(U, params={"partNumber": "HFS5-4040"}, headers=H, timeout=20)
print("     -> %d  %s" % (r.status_code, (r.status_code == 200 and "200-OK" or (r.json().get("errorList") or [{}])[0].get("errorCode", "?"))))
print("  核 ③：只走 query（不带 header）")
r = requests.get(U, params={"partNumber": "HFS5-4040", "applicationId": APP}, headers=H, timeout=20)
print("     -> %d  %s" % (r.status_code, (r.status_code == 200 and "200-OK" or (r.json().get("errorList") or [{}])[0].get("errorCode", "?"))))
print("  核 ④：两者都带")
r = requests.get(U, params={"partNumber": "HFS5-4040", "applicationId": APP},
                 headers=dict(H, applicationId=APP), timeout=20)
print("     -> %d  %s" % (r.status_code, (r.status_code == 200 and "200-OK" or (r.json().get("errorList") or [{}])[0].get("errorCode", "?"))))