package io.kindo.hub.infrastructure.iface;

import io.kindo.hub.infrastructure.po.Image;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.CrudRepository;
import org.springframework.data.repository.query.Param;

public interface ImageRepository extends CrudRepository<Image, Long>{
    Image findOneByUniqueName(String uniqueName);

    @Query("SELECT i FROM Image i WHERE (i.isprivate = 0 OR i.isprivate = :isprivate) AND  i.uniqueName LIKE :uniqueName")
    Page<Image> findByUniqueName(@Param("isprivate") long isprivate, @Param("uniqueName") String uniqueName, Pageable pageable);
}
