package com.exemplo.api.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "conversas")
public class Conversa {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(columnDefinition = "text")
    private String mensagem;

    @Column(columnDefinition = "text")
    private String resposta;

    private LocalDateTime dataHora = LocalDateTime.now();

    // getters e setters
    public Long getId() { return id; }
    public String getMensagem() { return mensagem; }
    public void setMensagem(String mensagem) { this.mensagem = mensagem; }
    public String getResposta() { return resposta; }
    public void setResposta(String resposta) { this.resposta = resposta; }
    public LocalDateTime getDataHora() { return dataHora; }
    public void setDataHora(LocalDateTime dataHora) { this.dataHora = dataHora; }
}
