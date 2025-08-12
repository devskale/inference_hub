from flask import Flask, request, Response
import requests
from OpenSSL import SSL

app = Flask(__name__)
TARGET_API = "https://aqueduct.ai.datalab.tuwien.ac.at"

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    try:
        # Forward request to target API
        resp = requests.request(
            method=request.method,
            url=f"{TARGET_API}/{path}",
            headers={key: value for key, value in request.headers if key != 'Host'},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            timeout=30  # 30-second timeout
        )
        
        # Build response from target API
        response = Response(resp.content, resp.status_code)
        for key, value in resp.headers.items():
            if key.lower() not in ['content-encoding', 'transfer-encoding']:
                response.headers[key] = value
        return response
        
    except requests.exceptions.Timeout:
        return "Target API timeout", 504
    except requests.exceptions.ConnectionError:
        return "Target API connection failed", 502
    except Exception as e:
        return f"Proxy error: {str(e)}", 500

if __name__ == '__main__':
    context = SSL.Context(SSL.TLSv1_2_METHOD)
    context.use_privatekey_file('key.pem')
    context.use_certificate_file('cert.pem')
    app.run(host='0.0.0.0', port=443, ssl_context=context, threaded=True)