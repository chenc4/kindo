package io.kindo.hub.api.iface;


import io.kindo.hub.api.vo.AccountInfo;
import io.kindo.hub.api.vo.ImageInfo;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.servlet.ModelAndView;

import java.io.IOException;
import java.text.ParseException;
import java.util.List;

@Controller
@RequestMapping(value="/v1")
public interface RestfulAPI {
    @RequestMapping(value="/search", method = RequestMethod.GET)
    @ResponseBody
    List<ImageInfo> search(
            @RequestParam(value="q", required = false, defaultValue = "") String q,
            @RequestParam(value="page", required = false, defaultValue = "0") String page,
            @RequestParam(value="limit", required = false, defaultValue = "10") String limit,
            @CookieValue(value = "username", required = false) String username,
            @CookieValue(value = "token", required = false) String token
    );

    @RequestMapping(value="/pull", method = RequestMethod.GET)
    @ResponseBody
    ImageInfo pull(
            @RequestParam(value="uniqueName") String uniqueName,
            @RequestParam(value="code", required = false, defaultValue = "") String code
    );

    @RequestMapping(value="/register", method = RequestMethod.POST)
    @ResponseBody
    AccountInfo register(
            @RequestParam(value="username") String username,
            @RequestParam(value="password") String password
    );


    @RequestMapping(value="/push", method = RequestMethod.POST)
    @ResponseBody
    ImageInfo push(
            @RequestParam(value = "username") String username,
            @RequestParam(value = "token") String token,
            @RequestParam(value = "author") String author,
            @RequestParam(value = "name") String name,
            @RequestParam(value = "version") String version,
            @RequestParam(value = "website") String website,
            @RequestParam(value = "summary") String summary,
            @RequestParam(value = "license") String license,
            @RequestParam(value = "buildversion") String buildversion,
            @RequestParam(value = "buildtime") String buildtime,
            @RequestParam(value = "code", defaultValue = "") String code,
            @RequestParam(value = "file", required = true) MultipartFile file

    ) throws IOException, ParseException;

    @RequestMapping(value="/login", method = RequestMethod.POST)
    @ResponseBody
    AccountInfo login(
            @RequestParam(value="username") String username,
            @RequestParam(value="token") String token
    );

    @RequestMapping(value="/rm", method = RequestMethod.POST)
    @ResponseBody
    ImageInfo rm(
            @RequestParam(value = "username") String username,
            @RequestParam(value = "token") String token,
            @RequestParam(value="uniqueName") String uniqueName
    );
}
