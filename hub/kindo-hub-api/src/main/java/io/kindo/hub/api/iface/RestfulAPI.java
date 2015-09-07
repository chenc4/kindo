package io.kindo.hub.api.iface;


import io.kindo.hub.api.vo.AccountInfo;
import io.kindo.hub.api.vo.ImageInfo;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.text.ParseException;
import java.util.List;

@Controller
@RequestMapping(value="/v1")
public interface RestfulAPI {
    @RequestMapping(value="/search", method = RequestMethod.GET)
    @ResponseBody
    List<ImageInfo> search(
            @RequestParam(value="q", required = true) String q
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
}
