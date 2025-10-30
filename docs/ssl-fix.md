```
import ssl
import urllib.request

try:
    # Create non verified SSL context
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    # Install global "opener" with this SSL context
    https_handler = urllib.request.HTTPSHandler(context=ssl_context)
    opener = urllib.request.build_opener(https_handler)
    urllib.request.install_opener(opener)

    print("✅ Check global disable of SSL certificate.")
    print("🔒 Warning: This reduce security.")

except Exception as e:
    print(f"❌ Error try to disable SSL verification: {e}")
```