from OpenSSL import crypto
import os

def generate_self_signed_cert():
    # 生成密钥
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 2048)

    # 创建证书
    cert = crypto.X509()
    cert.get_subject().C = "CN"
    cert.get_subject().ST = "State"
    cert.get_subject().L = "City"
    cert.get_subject().O = "Organization"
    cert.get_subject().OU = "Organizational Unit"
    cert.get_subject().CN = "localhost"

    # 设置证书有效期
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(365*24*60*60)  # 1年有效期

    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha256')

    # 确保目录存在
    if not os.path.exists('ssl'):
        os.makedirs('ssl')

    # 写入证书和私钥
    with open("ssl/cert.pem", "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    with open("ssl/key.pem", "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))

if __name__ == '__main__':
    generate_self_signed_cert()
    print("证书已生成在 ssl 目录中") 