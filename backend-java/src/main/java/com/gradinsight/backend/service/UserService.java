package com.gradinsight.backend.service;

import com.gradinsight.backend.dto.UserDTO;
import com.gradinsight.backend.entity.User;
import com.gradinsight.backend.repository.UserRepository;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
public class UserService {

    private final UserRepository repo;
    private final PasswordEncoder passwordEncoder;

    public UserService(UserRepository repo, PasswordEncoder passwordEncoder) {
        this.repo = repo;
        this.passwordEncoder = passwordEncoder;
    }

    public Optional<User> findByUsername(String username) {
        return repo.findByUsername(username);
    }

    public UserDTO register(UserDTO dto) {
        User u = new User();
        u.setUsername(dto.getUsername());
        u.setPassword(passwordEncoder.encode(dto.getPassword()));
        u.setRole(dto.getRole() == null ? "user" : dto.getRole());
        // email: use provided or generate default
        u.setEmail(dto.getEmail() != null && !dto.getEmail().isBlank()
                ? dto.getEmail() : dto.getUsername() + "@gradinsight.com");
        u.setIsActive(true);
        User saved = repo.save(u);
        UserDTO out = new UserDTO();
        out.setId(saved.getId());
        out.setUsername(saved.getUsername());
        out.setEmail(saved.getEmail());
        out.setRole(saved.getRole());
        return out;
    }
}
