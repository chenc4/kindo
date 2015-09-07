package io.kindo.hub.infrastructure.iface;

import io.kindo.hub.infrastructure.po.Image;
import org.springframework.data.repository.CrudRepository;

import java.util.List;

public interface ImageRepository extends CrudRepository<Image, Long>{
    Image findOneByUniqueName(String uniqueName);
    List<Image> findByUniqueNameLike(String uniqueName);
}
