package io.kindo.hub.infrastructure.po;

import javax.persistence.*;
import java.util.Date;

@Entity
@Table(name = "images")
public class Image {
    @Id
    @GeneratedValue(strategy= GenerationType.AUTO)
    private long id;

    private String name;
    private String author;
    private String pusher;
    private String version;
    private String website;
    private String summary;
    private String license;
    private String path;
    private long size;
    private String code;
    private String uniqueName;
    private int buildversion = 1;
    private Date buildtime;
    private Date createtime;


    public long getId() {
        return id;
    }

    public void setId(long id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getAuthor() {
        return author;
    }

    public void setAuthor(String author) {
        this.author = author;
    }

    public String getPusher() {
        return pusher;
    }

    public void setPusher(String pusher) {
        this.pusher = pusher;
    }

    public String getVersion() {
        return version;
    }

    public void setVersion(String version) {
        this.version = version;
    }

    public String getWebsite() {
        return website;
    }

    public void setWebsite(String website) {
        this.website = website;
    }

    public String getSummary() {
        return summary;
    }

    public void setSummary(String summary) {
        this.summary = summary;
    }

    public String getLicense() {
        return license;
    }

    public void setLicense(String license) {
        this.license = license;
    }

    public String getPath() {
        return path;
    }

    public void setPath(String path) {
        this.path = path;
    }

    public long getSize() {
        return size;
    }

    public void setSize(long size) {
        this.size = size;
    }

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public String getUniqueName() {
        return uniqueName;
    }

    public void setUniqueName(String uniqueName) {
        this.uniqueName = uniqueName;
    }

    public int getBuildversion() {
        return buildversion;
    }

    public void setBuildversion(int buildversion) {
        this.buildversion = buildversion;
    }

    public Date getBuildtime() {
        return buildtime;
    }

    public void setBuildtime(Date buildtime) {
        this.buildtime = buildtime;
    }

    public Date getCreatetime() {
        return createtime;
    }

    public void setCreatetime(Date createtime) {
        this.createtime = createtime;
    }

    @Override
    public String toString() {
        return "Image{" +
                "id=" + id +
                ", name='" + name + '\'' +
                ", author='" + author + '\'' +
                ", pusher='" + pusher + '\'' +
                ", version='" + version + '\'' +
                ", website='" + website + '\'' +
                ", summary='" + summary + '\'' +
                ", license='" + license + '\'' +
                ", path='" + path + '\'' +
                ", size=" + size +
                ", code='" + code + '\'' +
                ", uniqueName='" + uniqueName + '\'' +
                ", buildversion=" + buildversion +
                ", buildtime=" + buildtime +
                ", createtime=" + createtime +
                '}';
    }
}
