package io.kindo.hub.impl;

import io.kindo.hub.api.common.ErrorCode;
import io.kindo.hub.api.common.KindoUtils;
import io.kindo.hub.api.iface.RestfulAPI;
import io.kindo.hub.api.vo.AccountInfo;
import io.kindo.hub.api.vo.ImageInfo;
import io.kindo.hub.common.FileSystemStorage;
import io.kindo.hub.exception.KindoException;
import io.kindo.hub.infrastructure.iface.AccountRepository;
import io.kindo.hub.infrastructure.iface.ImageRepository;
import io.kindo.hub.infrastructure.po.Account;
import io.kindo.hub.infrastructure.po.Image;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

@RestController
public class DefaultRestfulAPI implements RestfulAPI {
    @Autowired
    private AccountRepository accountRepository;

    @Autowired
    private ImageRepository imageRepository;

    @Value("${kindo.storage.host}")
    private String host;

    @Value("${kindo.storage.folder}")
    private String folder;

    @Override
    public List<ImageInfo> search( @RequestParam(value = "q", required = true) String q) {
        if (q.isEmpty()) {
            throw new KindoException(ErrorCode.PARAMETER_EMPTY);
        }

        q = q.replace("%", "").replace("[", "").replace("]", "");
        q = "%" + q + "%";

        List<ImageInfo> imageInfos = new ArrayList<>();
        List<Image> images = imageRepository.findByUniqueNameLike(q);
        for (Image image : images) {
            ImageInfo imageInfo = new ImageInfo();
            imageInfo.setPusher(image.getPusher());
            imageInfo.setBuildtime(image.getBuildtime());
            imageInfo.setName(image.getUniqueName());
            imageInfo.setSize(image.getSize());
            imageInfo.setVersion(image.getVersion());
            imageInfos.add(imageInfo);
        }
        return imageInfos;
    }

    @Override
    public ImageInfo pull(
            @RequestParam(value = "uniqueName") String uniqueName,
            @RequestParam(value="code", required = false, defaultValue = "") String code
    ) {
        if (uniqueName.isEmpty()) {
            throw new KindoException(ErrorCode.PARAMETER_EMPTY);
        }

        if (uniqueName.contains("%s") || uniqueName.contains("[") || uniqueName.contains("]")) {
            throw new KindoException(ErrorCode.PARAMETER_INVALID);
        }

        Image image = imageRepository.findOneByUniqueName(uniqueName);
        if (image == null) {
            throw new KindoException(ErrorCode.IMAGE_NOT_FOUND);
        }

        if (!code.equals(image.getCode())) {
            throw new KindoException(ErrorCode.CODE_NEEDED);
        }

        if (!host.startsWith("http://") && !host.startsWith("https://")) {
            host = String.format("http://%s", host);
        }

        if (host.endsWith("/")) {
            host = host.substring(0, host.lastIndexOf("/"));
        }

        ImageInfo imageInfo = new ImageInfo();
        imageInfo.setPusher(image.getPusher());
        imageInfo.setBuildtime(image.getBuildtime());
        imageInfo.setName(image.getUniqueName());
        imageInfo.setSize(image.getSize());
        imageInfo.setUrl(String.format("%s/%s", host, image.getPath()));
        imageInfo.setVersion(image.getVersion());

        return imageInfo;
    }

    @Override
    public AccountInfo register(@RequestParam(value = "username") String username, @RequestParam(value = "password") String password) {
        if (username.isEmpty() || password.isEmpty()) {
            throw new KindoException(ErrorCode.PARAMETER_EMPTY);
        }

        if (username.matches("[^a-zA-Z0-9]") || username.equals("anonymous")) {
            throw new KindoException(ErrorCode.PARAMETER_INVALID);
        }

        Account account = accountRepository.findOneByUsername(username);
        if (account != null){
            throw new KindoException(ErrorCode.ACCOUNT_EXISTED);
        }

        account = new Account();
        account.setUsername(username);
        account.setPassword(KindoUtils.encode(password));
        account.setCreatetime(new Date());

        account = accountRepository.save(account);
        if (account == null) {
            throw  new KindoException(ErrorCode.SYSTEM_ERROR);
        }

        AccountInfo accountInfo = new AccountInfo();
        accountInfo.setUid(account.getId());
        accountInfo.setUsername(account.getUsername());
        return accountInfo;
    }

    @Override
    public ImageInfo push(
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
            @RequestParam(value = "code") String code,
            @RequestParam(value = "file", required = true) MultipartFile file
    ) throws IOException, ParseException {
        if (username.isEmpty() || token.isEmpty()) {
            throw new KindoException(ErrorCode.PARAMETER_EMPTY);
        }

        if (!code.isEmpty() && code.length() != 6) {
            throw new KindoException(ErrorCode.PARAMETER_INVALID);
        }

        if (!author.isEmpty() && author.matches("[^a-zA-Z0-9]")) {
            throw new KindoException(ErrorCode.PARAMETER_INVALID);
        }

        if (!name.isEmpty() && name.matches("[^a-zA-Z0-9-_]")) {
            throw new KindoException(ErrorCode.PARAMETER_INVALID);
        }

        if (!version.isEmpty() && version.matches("[^0-9\\.]")) {
            throw new KindoException(ErrorCode.PARAMETER_INVALID);
        }

        Account account = accountRepository.findOneByUsername(username);
        if (account == null || !token.equals(account.getPassword())){
            throw new KindoException(ErrorCode.PERMISSION_DENIED);
        }

        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        Date date = sdf.parse(buildtime);

        String filePath = KindoUtils.getFilePath("ki");
        String target = String.format("%s/%s", folder, filePath);
        if (!FileSystemStorage.upload(file.getBytes(), target)) {
            throw new KindoException(ErrorCode.SYSTEM_ERROR);
        }

        String uniqueName = String.format("%s/%s:%s", author, name, version);
        Image image = imageRepository.findOneByUniqueName(uniqueName);
        if (image != null) {
            throw new KindoException(ErrorCode.IMAGE_EXISTED);
        }

        image = new Image();
        image.setVersion(version);
        image.setBuildtime(date);
        image.setCreatetime(new Date());
        image.setPath(filePath);
        image.setAuthor(author);
        image.setCode(code);
        image.setBuildversion(Integer.parseInt(buildversion));
        image.setLicense(license);
        image.setName(name);
        image.setPusher(username);
        image.setSize(file.getSize());
        image.setSummary(summary);
        image.setWebsite(website);
        image.setUniqueName(uniqueName);

        image = imageRepository.save(image);
        if (image == null) {
            throw new KindoException(ErrorCode.SYSTEM_ERROR);
        }

        if (!host.startsWith("http://") && !host.startsWith("https://")) {
            host = String.format("http://%s", host);
        }

        if (host.endsWith("/")) {
            host = host.substring(0, host.lastIndexOf("/"));
        }

        ImageInfo imageInfo = new ImageInfo();
        imageInfo.setVersion(image.getVersion());
        imageInfo.setUrl(String.format("%s/%s", host, image.getPath()));
        imageInfo.setBuildtime(image.getBuildtime());
        imageInfo.setPusher(image.getPusher());
        imageInfo.setSize(image.getSize());
        imageInfo.setName(image.getUniqueName());

        return imageInfo;
    }

    @Override
    public AccountInfo login(@RequestParam(value = "username") String username, @RequestParam(value = "token") String token) {
        if (username.isEmpty() || token.isEmpty()) {
            throw new KindoException(ErrorCode.PARAMETER_EMPTY);
        }

        Account account = accountRepository.findOneByUsername(username);
        if (account == null || !token.equals(account.getPassword())){
            throw new KindoException(ErrorCode.PERMISSION_DENIED);
        }

        AccountInfo accountInfo = new AccountInfo();
        accountInfo.setUsername(username);
        accountInfo.setUid(account.getId());
        return accountInfo;
    }

    @Override
    public ImageInfo rm(
            @RequestParam(value = "username") String username,
            @RequestParam(value = "token") String token,
            @RequestParam(value = "uniqueName") String uniqueName
    ) {
        if (uniqueName.isEmpty() || username.isEmpty() || token.isEmpty()) {
            throw new KindoException(ErrorCode.PARAMETER_EMPTY);
        }

        Account account = accountRepository.findOneByUsername(username);
        if (account == null || !token.equals(account.getPassword())){
            throw new KindoException(ErrorCode.PERMISSION_DENIED);
        }

        Image image = imageRepository.findOneByUniqueName(uniqueName);
        if (image == null) {
            throw new KindoException(ErrorCode.IMAGE_NOT_FOUND);
        }

        if (!image.getPusher().equals(username)) {
            throw new KindoException(ErrorCode.PERMISSION_DENIED);
        }

        imageRepository.delete(image);

        ImageInfo imageInfo = new ImageInfo();
        imageInfo.setVersion(image.getVersion());
        imageInfo.setUrl(String.format("%s/%s", host, image.getPath()));
        imageInfo.setBuildtime(image.getBuildtime());
        imageInfo.setPusher(image.getPusher());
        imageInfo.setSize(image.getSize());
        imageInfo.setName(image.getUniqueName());

        return imageInfo;
    }
}
