class AttendanceRecord {
  AttendanceRecord({
    required this.id,
    required this.courseId,
    required this.date,
    required this.studentId,
    required this.present,
    required this.teacherId,
  });

  final String id;
  final String courseId;
  final String date;
  final String studentId;
  final bool present;
  final String teacherId;

  factory AttendanceRecord.fromJson(Map<String, dynamic> json) {
    return AttendanceRecord(
      id: json['id'] as String,
      courseId: json['course_id'] as String,
      date: json['date'] as String,
      studentId: json['student_id'] as String,
      present: json['present'] as bool,
      teacherId: json['teacher_id'] as String,
    );
  }
}
