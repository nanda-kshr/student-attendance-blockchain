class SubjectAttendance {
  SubjectAttendance({
    required this.subjectCode,
    required this.attendancePercentage,
    required this.totalClasses,
    required this.attendedClasses,
  });

  final String subjectCode;
  final double attendancePercentage;
  final int totalClasses;
  final int attendedClasses;

  factory SubjectAttendance.fromJson(Map<String, dynamic> json) {
    return SubjectAttendance(
      subjectCode: (json['subject_code'] ?? '') as String,
      attendancePercentage: (json['attendance_percentage'] ?? 0).toDouble(),
      totalClasses: (json['total_classes'] ?? 0) as int,
      attendedClasses: (json['attended_classes'] ?? 0) as int,
    );
  }
}
