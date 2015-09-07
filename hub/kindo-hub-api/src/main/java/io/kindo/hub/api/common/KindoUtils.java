package io.kindo.hub.api.common;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.apache.commons.codec.digest.DigestUtils;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.math.BigInteger;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Calendar;
import java.util.UUID;

public class KindoUtils {
    private final static Logger logger = LoggerFactory.getLogger(KindoUtils.class);

    public static String getFilePath(String extension) {
        Calendar cal = Calendar.getInstance();

        return String.format(
                "kindo/%s/%s/%s/%s/%s/%s/%s.%s",
                cal.get(Calendar.YEAR),
                cal.get(Calendar.MONTH),
                cal.get(Calendar.DATE),
                cal.get(Calendar.HOUR),
                cal.get(Calendar.MINUTE),
                cal.get(Calendar.SECOND),
                UUID.randomUUID().toString(),
                extension
                );
    }

    public static String encode(byte[] bytes) {
        String value = "";
        try {
            MessageDigest md5 = MessageDigest.getInstance("MD5");
            md5.update(bytes);
            BigInteger bi = new BigInteger(1, md5.digest());
            value = bi.toString(16);
        } catch (NoSuchAlgorithmException e) {
            logger.error("getFileMD5.NoSuchAlgorithmException", e);
        }
        return value;
    }

    public static String encode(File file) {
        try (InputStream stream = new FileInputStream(file)) {
            return DigestUtils.md5Hex(stream);
        } catch (IOException e) {
            logger.error(e.getMessage(), e);
        }
        return "";
    }

    public static String encode(String value) {
        return encode(value.getBytes());
    }
}
