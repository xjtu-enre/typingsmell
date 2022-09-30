import hashlib


class SHA256:
    @classmethod
    def encode_hash(cls, temp: str) -> str:
        secret = hashlib.sha256()
        secret.update(temp.encode(encoding='utf-8'))

        return secret.hexdigest()


class MD5:
    @classmethod
    def encode_file(cls, file_path: str) -> str:
        with open(file_path, 'rb') as f:
            md5 = hashlib.md5()
            while True:
                d = f.read(8096)
                if not d:
                    break
                md5.update(d)
            hash_code = md5.hexdigest()
            return str(hash_code).lower()
