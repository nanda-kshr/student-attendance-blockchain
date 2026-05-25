class Student {
  Student({required this.id, required this.email, required this.role});

  final String id;
  final String email;
  final String role;

  factory Student.fromJson(Map<String, dynamic> json) {
    return Student(
      id: json['id'] as String,
      email: json['email'] as String,
      role: json['role'] as String,
    );
  }
}
