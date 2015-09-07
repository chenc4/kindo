package io.kindo.hub.infrastructure.iface;

import io.kindo.hub.infrastructure.po.Account;
import org.springframework.data.repository.CrudRepository;

public interface AccountRepository extends CrudRepository<Account, Long> {
    Account findOneByUsername(String username);
}
