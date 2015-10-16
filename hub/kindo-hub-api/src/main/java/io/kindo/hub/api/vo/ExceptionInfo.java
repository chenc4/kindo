package io.kindo.hub.api.vo;

import io.kindo.hub.api.common.ErrorCode;

public class ExceptionInfo {
    private String code;
    private String msg;

    public ExceptionInfo() {
        this(ErrorCode.SYSTEM_ERROR);
    }

    public ExceptionInfo(ErrorCode error) {
        this.code = error.getCode();
        this.msg = error.getMessage();
    }

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public String getMsg() {
        return msg;
    }

    public void setMsg(String msg) {
        this.msg = msg;
    }

    @Override
    public String toString() {
        return "ExceptionInfo{" +
                "code='" + code + '\'' +
                ", msg='" + msg + '\'' +
                '}';
    }
}
