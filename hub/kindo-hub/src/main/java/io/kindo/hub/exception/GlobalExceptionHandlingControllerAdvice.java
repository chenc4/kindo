package io.kindo.hub.exception;

import io.kindo.hub.api.common.ErrorCode;
import io.kindo.hub.api.vo.ExceptionInfo;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.MissingServletRequestParameterException;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.servlet.NoHandlerFoundException;

import java.nio.file.AccessDeniedException;


@ControllerAdvice
public class GlobalExceptionHandlingControllerAdvice {
    protected Logger logger = LoggerFactory.getLogger(GlobalExceptionHandlingControllerAdvice.class);

    @ExceptionHandler(value = KindoException.class)
    @ResponseStatus(HttpStatus.OK)
    @ResponseBody
    public ExceptionInfo cyStorgesExceptionHandler(KindoException ex) {
        logger.error(ex.getMessage());
        ExceptionInfo exceptionInfo = new ExceptionInfo();
        exceptionInfo.setCode(ex.getCode());
        exceptionInfo.setMsg(ex.getMessage());

        logger.error("cyStorgesExceptionHandler", ex);

        return exceptionInfo;
    }

    @ExceptionHandler(value = NoHandlerFoundException.class)
    @ResponseStatus(HttpStatus.OK)
    @ResponseBody
    public ExceptionInfo noHandlerFoundExceptionHandler(NoHandlerFoundException ex) {
        logger.error(ex.getMessage());

        ExceptionInfo exceptionInfo = new ExceptionInfo();
        exceptionInfo.setCode(ErrorCode.REQUEST_API_OR_MODULE_NOT_FOUND.getCode());
        exceptionInfo.setMsg(ErrorCode.REQUEST_API_OR_MODULE_NOT_FOUND.getMessage());

        logger.error("noHandlerFoundExceptionHandler", ex);
        return exceptionInfo;
    }

    @ExceptionHandler(value = NoSuchMethodException.class)
    @ResponseStatus(HttpStatus.OK)
    @ResponseBody
    public ExceptionInfo noSuchMethodExceptionHandler(NoSuchMethodException ex) {
        logger.error(ex.getMessage());

        ExceptionInfo exceptionInfo = new ExceptionInfo();
        exceptionInfo.setCode(ErrorCode.HTTP_METHOD_NOT_SUPPORTED.getCode());
        exceptionInfo.setMsg(ErrorCode.HTTP_METHOD_NOT_SUPPORTED.getMessage());

        logger.error("noSuchMethodExceptionHandler", ex);
        return exceptionInfo;
    }

    @ExceptionHandler(value = AccessDeniedException.class)
    @ResponseStatus(HttpStatus.OK)
    @ResponseBody
    public ExceptionInfo accessDeniedExceptionHandler(AccessDeniedException ex) {
        logger.error(ex.getMessage());

        ExceptionInfo exceptionInfo = new ExceptionInfo();
        exceptionInfo.setCode(ErrorCode.PERMISSION_DENIED.getCode());
        exceptionInfo.setMsg(ErrorCode.PERMISSION_DENIED.getMessage());

        logger.error("accessDeniedExceptionHandler", ex);
        return exceptionInfo;
    }

    @ExceptionHandler(value = MissingServletRequestParameterException.class)
    @ResponseStatus(HttpStatus.OK)
    @ResponseBody
    public ExceptionInfo missingServletRequestParameterExceptionHandler(MissingServletRequestParameterException ex) {
        logger.error(ex.getMessage());

        ExceptionInfo exceptionInfo = new ExceptionInfo();
        exceptionInfo.setCode(ErrorCode.MISS_REQUIRED_PARAMETER.getCode());
        exceptionInfo.setMsg(ErrorCode.MISS_REQUIRED_PARAMETER.getMessage());

        logger.error("missingServletRequestParameterExceptionHandler", ex);
        return exceptionInfo;
    }

    @ExceptionHandler(value = NumberFormatException.class)
    @ResponseStatus(HttpStatus.OK)
    @ResponseBody
    public ExceptionInfo numberFormatExceptionHandler(NumberFormatException ex) {
        logger.error(ex.getMessage());

        ExceptionInfo exceptionInfo = new ExceptionInfo();
        exceptionInfo.setCode(ErrorCode.PARAMETER_INVALID.getCode());
        exceptionInfo.setMsg(ErrorCode.PARAMETER_INVALID.getMessage());

        logger.error("numberFormatExceptionHandler", ex);
        return exceptionInfo;
    }

    @ExceptionHandler(value = Exception.class)
    @ResponseStatus(HttpStatus.OK)
    @ResponseBody
    public ExceptionInfo exceptionHandler(Exception ex) {
        logger.error(ex.getMessage());

        ExceptionInfo exceptionInfo = new ExceptionInfo();
        exceptionInfo.setCode(ErrorCode.SYSTEM_ERROR.getCode());
        exceptionInfo.setMsg(ErrorCode.SYSTEM_ERROR.getMessage());

        logger.error("exceptionHandler", ex);
        return exceptionInfo;
    }
}
