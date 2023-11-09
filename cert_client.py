import ecdsa
import requests
import time
import sys

ip = sys.argv[1]

# 生成ECDSA私钥和公钥
sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
vk = sk.get_verifying_key()

start_time = time.time()  # 得到开始时间
# 获取服务器发来的挑战字符串并进行签名
challenge_string = requests.get(f"http://{ip}:18080/challenge").text
signature = sk.sign(challenge_string.encode())

# 发送签名和公钥给服务器进行验证
response = requests.post(f"http://{ip}:18080/verify", 
            data={'public_key': vk.to_string().hex(), 'signature': signature.hex()})

print(response.text)

end_time = time.time()  # 得到结束时间

print(f"The verification costs {end_time - start_time} seconds.")