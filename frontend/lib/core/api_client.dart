import 'dart:convert';

import 'package:http/http.dart' as http;

class ApiClient {
  ApiClient({http.Client? httpClient}) : _httpClient = httpClient ?? http.Client();

  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.250.55.19:4000',
  );

  final http.Client _httpClient;

  Future<dynamic> get(
    String path, {
    String? token,
    Map<String, String>? query,
  }) async {
    final uri = Uri.parse('$baseUrl$path').replace(queryParameters: query);
    final response = await _httpClient.get(uri, headers: _headers(token));
    return _handleResponse(response);
  }

  Future<dynamic> post(
    String path, {
    String? token,
    Map<String, dynamic>? body,
  }) async {
    final uri = Uri.parse('$baseUrl$path');
    final response = await _httpClient.post(
      uri,
      headers: _headers(token),
      body: jsonEncode(body ?? {}),
    );
    return _handleResponse(response);
  }

  Future<dynamic> put(
    String path, {
    String? token,
    Map<String, dynamic>? body,
  }) async {
    final uri = Uri.parse('$baseUrl$path');
    final response = await _httpClient.put(
      uri,
      headers: _headers(token),
      body: jsonEncode(body ?? {}),
    );
    return _handleResponse(response);
  }

  Future<dynamic> delete(
    String path, {
    String? token,
  }) async {
    final uri = Uri.parse('$baseUrl$path');
    final response = await _httpClient.delete(uri, headers: _headers(token));
    return _handleResponse(response);
  }

  Map<String, String> _headers(String? token) {
    final headers = <String, String>{'Content-Type': 'application/json'};
    if (token != null) {
      headers['Authorization'] = 'Bearer $token';
    }
    return headers;
  }

  dynamic _handleResponse(http.Response response) {
    final body = response.body.isNotEmpty ? jsonDecode(response.body) : {};
    if (response.statusCode < 200 || response.statusCode >= 300) {
      final message = body is Map && body['detail'] is String
          ? body['detail'] as String
          : 'Request failed (${response.statusCode})';
      throw Exception(message);
    }
    return body;
  }
}
