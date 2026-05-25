import 'dart:convert';

import 'package:flutter/material.dart';

import 'api_client.dart';

class AuthState extends ChangeNotifier {
  AuthState({ApiClient? apiClient}) : _api = apiClient ?? ApiClient();

  final ApiClient _api;
  String? _token;
  String? _role;
  String? _userId;
  String? _email;

  bool get isAuthenticated => _token != null;
  String? get token => _token;
  String? get role => _role;
  String? get userId => _userId;
  String? get email => _email;

  Future<void> login(String email, String password) async {
    final data = await _api.post(
      '/auth/login',
      body: {'email': email, 'password': password},
    ) as Map<String, dynamic>;
    final accessToken = data['access_token'] as String?;
    if (accessToken == null) {
      throw Exception('Invalid login response');
    }

    final payload = _decodeJwt(accessToken);
    _token = accessToken;
    _role = payload['role'] as String?;
    _userId = payload['sub'] as String?;
    _email = email;
    notifyListeners();
  }

  Future<void> register(String email, String password, String role) async {
    await _api.post(
      '/auth/register',
      body: {'email': email, 'password': password, 'role': role},
    );
    await login(email, password);
  }

  void logout() {
    _token = null;
    _role = null;
    _userId = null;
    _email = null;
    notifyListeners();
  }

  Map<String, dynamic> _decodeJwt(String token) {
    final parts = token.split('.');
    if (parts.length != 3) {
      throw Exception('Invalid token');
    }
    final payload = base64Url.normalize(parts[1]);
    final decoded = utf8.decode(base64Url.decode(payload));
    return jsonDecode(decoded) as Map<String, dynamic>;
  }
}

class AuthScope extends InheritedNotifier<AuthState> {
  const AuthScope({super.key, required AuthState authState, required Widget child})
      : super(notifier: authState, child: child);

  static AuthState of(BuildContext context) {
    final scope = context.dependOnInheritedWidgetOfExactType<AuthScope>();
    if (scope == null) {
      throw Exception('AuthScope not found');
    }
    return scope.notifier!;
  }
}
