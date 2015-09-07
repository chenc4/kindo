package io.kindo.hub.api.common;

public enum ErrorCode {
    SYSTEM_ERROR("10005000", "System error"),
    SERVICE_UNAVAILABLE("10005001", "Service unavailable"),
    SERVICE_MODULE_UNAVAILABLE("", "Service module unavailable"),
    REQUEST_EXPIRED("10005003", "request expired"),
    PERMISSION_DENIED_NEED_A_HIGH_LEVEL_APPKEY("10004030", "Permission denied, need a high level appkey"),
    PERMISSION_DENIED_NEED_A_SPECIAL_LEVEL_APPKEY("010004031", "Permission denied, need a special level appkey"),
    PERMISSION_DENIED("010004032", "Permission denied"),
    IP_REQUESTS_OUT_OF_RATE_LIMIT("010004033", "IP requests out of rate limit"),
    INVALID_REQUEST("010004034", "Invalid request"),
    THE_APPKEY_MISSED("010004035", "The appkey missed"),
    SERVICE_NOT_REGISTED("010004036", "Service not registed"),
    TOKEN_EXPIRED("010004037", "Token expired"),
    PARAMETER_INVALID("010004000", "Parameter invalid"),
    MISS_REQUIRED_PARAMETER("010004001", "Miss required parameter, see doc for more info"),
    TOO_MANY_PARAMETERS("010004002", "Too many parameters"),
    PARAMETER_EMPTY("010004003", "Parameter empty"),
    PARAMETER_FORMATER_INVALID("010004004", "Parameter formater invalid"),
    PARAMETER_ENCODING_INVALID("010004005", "Parameter encoding invalid"),
    PARAMETER_LENGTH_OVER_LIMIT("010004006", "Parameter length over limit"),
    REQUEST_API_OR_MODULE_NOT_FOUND("010004040", "Request api / module not found"),
    HTTP_METHOD_NOT_SUPPORTED("010004041", "HTTP method is not suported for this request"),
    CODE_NEEDED("040014000", "Extraction code needed"),
    ACCOUNT_EXISTED("040014001", "account existed"),
    IMAGE_NOT_FOUND("040014040", "image not found"),
    IMAGE_EXISTED("040014002", "image existed");

    private String code;
    private String message;

    ErrorCode(String code, String msg) {
        this.code = code;
        this.message = msg;
    }
    public String getCode() {
        return this.code;
    }

    public String getMessage() {
        return this.message;
    }
}
