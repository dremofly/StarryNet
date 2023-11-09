from flask import Flask, request
import os
import secrets
import ecdsa

app = Flask(__name__)

@app.route('/challenge', methods=['GET'])
def challenge():
    global challenge_string # 为简化示例，在全局中定义
    challenge_string = secrets.token_hex(16) # 生成随机字符串
    return challenge_string 

@app.route('/verify', methods=['POST'])
def verify():
    public_key_data = request.values.get('public_key')  # 需要客户端上传其公钥
    signature = bytes.fromhex(request.values.get('signature')) # 签名是16进制字符串

    # 获得客户端的公钥
    vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(public_key_data), curve=ecdsa.SECP256k1)

    if vk.verify(signature, challenge_string.encode()):
        return 'Verified'
    else:
        return 'Not Verified'

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=18080)
