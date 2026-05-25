class Course {
  Course({
    required this.id,
    required this.name,
    required this.code,
    required this.teacherId,
  });

  final String id;
  final String name;
  final String code;
  final String teacherId;

  factory Course.fromJson(Map<String, dynamic> json) {
    return Course(
      id: json['id'] as String,
      name: json['name'] as String,
      code: json['code'] as String,
      teacherId: json['teacher_id'] as String,
    );
  }
}
