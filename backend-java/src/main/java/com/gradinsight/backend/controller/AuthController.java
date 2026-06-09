package com.gradinsight.backend.controller;

import com.gradinsight.backend.dto.AuthResponse;
import com.gradinsight.backend.dto.UserDTO;
import com.gradinsight.backend.service.UserService;
import com.gradinsight.backend.security.JwtUtil;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

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
        var userOpt = userService.findByUsername(user.getUsername());
        if (userOpt.isEmpty()) {
            // 用户不存在也用 401，避免泄露用户是否存在
            return ResponseEntity.status(401)
                    .body(Map.of("detail", "用户名或密码错误"));
        }
        var u = userOpt.get();
        if (!passwordEncoder.matches(user.getPassword(), u.getPassword())) {
            return ResponseEntity.status(401)
                    .body(Map.of("detail", "用户名或密码错误"));
        }
        String token = jwtUtil.generateToken(u.getUsername());
        return ResponseEntity.ok(new AuthResponse(token));
    }

    @PostMapping("/register")
    public ResponseEntity<?> register(@RequestBody UserDTO user) {
        try {
            UserDTO saved = userService.register(user);
            return ResponseEntity.ok(saved);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.CONFLICT)
                    .body(Map.of("detail", e.getMessage()));
        }
    }

    @GetMapping("/me")
    public ResponseEntity<?> me(@RequestHeader(name = "Authorization", required = false) String auth) {
        if (auth == null || !auth.startsWith("Bearer "))
            return ResponseEntity.status(401).body(Map.of("detail", "未登录"));

        String token = auth.substring(7);
        try {
            if (!jwtUtil.validateToken(token))
                return ResponseEntity.status(401).body(Map.of("detail", "token 无效或已过期"));

            String username = jwtUtil.extractUsername(token);
            var userOpt = userService.findByUsername(username);
            if (userOpt.isEmpty())
                return ResponseEntity.status(404).body(Map.of("detail", "用户不存在"));

            var u = userOpt.get();
            UserDTO dto = new UserDTO();
            dto.setId(u.getId());
            dto.setUsername(u.getUsername());
            dto.setRole(u.getRole());
            return ResponseEntity.ok(dto);
        } catch (Exception e) {
            return ResponseEntity.status(401).body(Map.of("detail", "token 解析失败"));
        }
    }
}
