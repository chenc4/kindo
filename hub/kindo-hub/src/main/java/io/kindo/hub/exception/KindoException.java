package io.kindo.hub.exception;

import io.kindo.hub.api.common.ErrorCode;

public class KindoException extends RuntimeException{
    private String code;

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public KindoException() {
        super();
    }

    public KindoException(String message) {
        super(message);
    }

    public KindoException(String code, String message) {
        super(message);
        this.code = code;
    }

    public KindoException(ErrorCode errorCode) {
        super(errorCode.getMessage());
        this.code = errorCode.getCode();
    }
}
