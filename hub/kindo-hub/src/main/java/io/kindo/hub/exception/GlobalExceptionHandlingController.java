package io.kindo.hub.exception;

import io.kindo.hub.api.common.ErrorCode;
import io.kindo.hub.api.vo.ExceptionInfo;
import org.springframework.boot.autoconfigure.web.ErrorController;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

/**
 * Created by shenghe on 2015/10/16.
 */
@Controller
public class GlobalExceptionHandlingController implements ErrorController{
    @RequestMapping(value="/error", method = RequestMethod.GET)
    @ResponseBody
    ExceptionInfo error(){
        return new ExceptionInfo(ErrorCode.REQUEST_API_OR_MODULE_NOT_FOUND);
    }

    @Override
    public String getErrorPath() {
        return "/error";
    }
}
