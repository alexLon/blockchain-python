import sys
sys.path.append('/dev/blockchain-python')
from Blockchain.backend.core.EllipticCurve.EllipticCurve import Sha256Point
from Blockchain.backend.core.database.database import AccountDB
import secrets
from Blockchain.backend.util.util import hash160
from Blockchain.backend.util.util import hash256

class Account:
    """
    This class crates the private and public keys, as well as addresses.
    The private key is a single unsigned 256 bit integer and randomly generated
    The public is derived from the private key and is compressed. They contain a 0x02 0x04 prefix
    """

    def createKeys(self):
        # this corresponds to 2 points on an elliptic curve
        Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
        Gy = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8

        G = Sha256Point(Gx, Gy)

        self.privateKey = secrets.randbits(256)
        unCompressedPublicKey = self.privateKey * G
        xPoint = unCompressedPublicKey.x
        yPoint = unCompressedPublicKey.y

        if yPoint.num % 2 == 0:
            compressesKey = b'\x02' + xPoint.num.to_bytes(32, 'big')
        else:
            compressesKey = b'\x03' + xPoint.num.to_bytes(32, 'big')

        hsh160 = hash160(compressesKey)
        
        """Prefix for Mainnet"""
        mainPrefix = b'\x00'

        newAddr = mainPrefix + hsh160

        """Checksum"""
        checkSum = hash256(newAddr)[:4]

        newAddr = newAddr + checkSum
        BASE58_ALPHABET = '123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

        count = 0

        for c in newAddr:
            if c == 0:
                count += 1
            else:
                break
        
        num = int.from_bytes(newAddr, 'big')
        prefix = '1' * count
        
        result = ''

        while num > 0:
            num, mod = divmod(num, 58)
            result = BASE58_ALPHABET[mod] + result

        self.publicAddress = prefix + result

        print(f"Private key is {self.privateKey}")
        print(f"Public key is {self.publicAddress}")


if __name__ == '__main__':
    acct = Account()
    acct.createKeys()
    AccountDB().write([acct.__dict__])
