package com.exemplo.api.repositorio;

import com.exemplo.api.model.Conversa;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface RepositorioConversa extends JpaRepository<Conversa, Long> {}
