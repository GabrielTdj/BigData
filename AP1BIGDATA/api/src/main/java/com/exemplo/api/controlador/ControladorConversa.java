package com.exemplo.api.controlador;

import com.exemplo.api.model.Conversa;
import com.exemplo.api.repositorio.RepositorioConversa;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/conversas")
public class ControladorConversa {

    private final RepositorioConversa repositorio;

    public ControladorConversa(RepositorioConversa repositorio) {
        this.repositorio = repositorio;
    }

    @PostMapping
    public Conversa salvar(@RequestBody Map<String, String> body) {
        Conversa c = new Conversa();
        c.setMensagem(body.get("mensagem"));
        c.setResposta(body.get("resposta"));
        return repositorio.save(c);
    }

    @GetMapping
    public List<Conversa> listar() {
        return repositorio.findAll();
    }
}
