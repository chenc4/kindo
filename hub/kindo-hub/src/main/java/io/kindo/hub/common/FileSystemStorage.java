package io.kindo.hub.common;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.*;

public class FileSystemStorage {
    protected final static Logger logger = LoggerFactory.getLogger(FileSystemStorage.class);

    public static boolean upload(byte[] bytes, String target) {
        BufferedOutputStream stream = null;
        try {
            File remoteFile = new File(target);
            File remoteParent = new File(remoteFile.getParent());
            if (!remoteParent.exists()) {
                remoteParent.mkdirs();
            }

            if (remoteFile.exists()) {
                remoteFile.delete();
            }

            stream = new BufferedOutputStream(new FileOutputStream(remoteFile));
            stream.write(bytes);

            return true;
        } catch (FileNotFoundException e) {
            logger.error("upload.FileNotFoundException", e);
        } catch (IOException e) {
            logger.error("upload.IOException", e);
        } finally {
            try {
                if (stream != null) {
                    stream.close();
                }
            } catch (IOException e) {
                logger.error("upload.IOException", e);
            }
        }

        return false;
    }

    public static String getExtensionName(String filename) {
        if ((filename != null) && (filename.length() > 0)) {
            int dot = filename.lastIndexOf('.');
            if ((dot >-1) && (dot < (filename.length() - 1))) {
                return filename.substring(dot + 1);
            }
        }
        return filename;
    }
}
