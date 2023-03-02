package org.ogios;

import org.bouncycastle.jce.provider.BouncyCastleProvider;

import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.security.Security;
import java.util.Base64;

public class Encrypt {
    static String aes_chars = "ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678";
    static int aes_chars_len = aes_chars.length();

    static {
        Security.addProvider(new BouncyCastleProvider());
    }

    public static String randomString(int length){
        StringBuilder retStr = new StringBuilder();
        for (int i=0; i<length; i++){
            int index = (int) Math.floor(Math.random() * aes_chars_len);
            retStr.append(aes_chars.charAt(index));
        }
        return retStr.toString();
    }

    public static String _encrypt(String password, String key0, String iv0){
        SecretKeySpec key = new SecretKeySpec(key0.strip().getBytes(StandardCharsets.UTF_8), "AES");
        IvParameterSpec iv = new IvParameterSpec(iv0.getBytes(StandardCharsets.UTF_8));
        try {
            Cipher cipher = Cipher.getInstance("AES/CBC/PKCS7Padding");
            cipher.init(Cipher.ENCRYPT_MODE, key, iv);
            byte[] encrypted = cipher.doFinal(password.getBytes(StandardCharsets.UTF_8));
            Base64.Encoder encoder = Base64.getEncoder();
            return encoder.encodeToString(encrypted);
        } catch (Exception e) {
            e.printStackTrace();
            return "";
        }
    }

    public static String encrypt(String password, String key0){
        return _encrypt(
                randomString(64) + password,
                key0,
                randomString(16)
        );
    }



//    public static void main(String[] args) {
//        System.out.println(encrypt("123456", "gxOYlTE45BB1NCMU"));
//    }

}
