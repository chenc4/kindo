package io.kindo.hub.exception;

import org.springframework.boot.autoconfigure.web.ErrorController;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller
public class GlobalExceptionControler implements ErrorController {
    private static final String ERROR_PATH = "/error";

    @RequestMapping(value=ERROR_PATH)
    public String handleError() throws NoSuchMethodException {
        throw new NoSuchMethodException();
    }

    @Override
    public String getErrorPath() {
        return ERROR_PATH;
    }
}
