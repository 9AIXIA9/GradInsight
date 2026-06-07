package com.gradinsight.backend.controller;

import com.gradinsight.backend.dto.AuthResponse;
import com.gradinsight.backend.dto.UserDTO;
import com.gradinsight.backend.entity.User;
import com.gradinsight.backend.service.UserService;
import com.gradinsight.backend.security.JwtUtil;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private final UserService userService;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;

    public AuthController(UserService userService, PasswordEncoder passwordEncoder, JwtUtil jwtUtil) {
        this.userService = userService;
        this.passwordEncoder = passwordEncoder;
        this.jwtUtil = jwtUtil;
    }

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody UserDTO user) {
        return userService.findByUsername(user.getUsername()).map(u -> {
            if (passwordEncoder.matches(user.getPassword(), u.getPassword())) {
                String token = jwtUtil.generateToken(u.getUsername());
                return ResponseEntity.ok(new AuthResponse(token));
            }
            return ResponseEntity.status(401).body("invalid credentials");
        }).orElse(ResponseEntity.status(404).body("user not found"));
    }

    @PostMapping("/register")
    public ResponseEntity<?> register(@RequestBody UserDTO user) {
        UserDTO saved = userService.register(user);
        return ResponseEntity.ok(saved);
    }

    @GetMapping("/me")
    public ResponseEntity<UserDTO> me(@RequestHeader(name = "Authorization", required = false) String auth) {
        // 简单实现：从 token 解出用户名并返回
        if (auth == null || !auth.startsWith("Bearer ")) return ResponseEntity.ok(null);
        String token = auth.substring(7);
        String username = jwtUtil.extractUsername(token);
        return userService.findByUsername(username).map(u -> {
            UserDTO dto = new UserDTO();
            dto.setId(u.getId());
            dto.setUsername(u.getUsername());
            dto.setRole(u.getRole());
            return ResponseEntity.ok(dto);
        }).orElse(ResponseEntity.notFound().build());
    }
}
