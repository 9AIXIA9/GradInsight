package com.gradinsight.backend.controller;

import com.gradinsight.backend.dto.UserDTO;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody UserDTO user) {
        // TODO: 实现认证逻辑（集成 Spring Security 或 Sa-Token）
        return ResponseEntity.ok("token-placeholder");
    }

    @PostMapping("/register")
    public ResponseEntity<?> register(@RequestBody UserDTO user) {
        // TODO: 保存用户到数据库
        return ResponseEntity.ok("registered");
    }

    @GetMapping("/me")
    public ResponseEntity<UserDTO> me() {
        // TODO: 根据 token 返回当前用户信息
        UserDTO u = new UserDTO();
        u.setUsername("demo");
        return ResponseEntity.ok(u);
    }
}
