import 'package:flutter/material.dart';

import '../core/api_client.dart';
import '../core/auth_state.dart';
import '../models/attendance.dart';
import '../models/course.dart';
import '../models/student.dart';
import '../models/subject_attendance.dart';

class AttendanceScreen extends StatefulWidget {
  const AttendanceScreen({super.key});

  @override
  State<AttendanceScreen> createState() => _AttendanceScreenState();
}

class _AttendanceScreenState extends State<AttendanceScreen> {
  final ApiClient _api = ApiClient();
  DateTime _selectedDate = DateTime.now();
  bool _isLoading = false;
  bool _isSaving = false;
  bool _didLoad = false;
  List<AttendanceRecord> _records = [];
  List<Course> _courses = [];
  Course? _selectedCourse;
  List<Student> _students = [];
  final Set<String> _presentStudentIds = {};
  List<SubjectAttendance> _subjectAttendance = [];

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (!_didLoad) {
      _didLoad = true;
      _loadCourses();
    }
  }

  Future<void> _pickDate() async {
    final date = await showDatePicker(
      context: context,
      initialDate: _selectedDate,
      firstDate: DateTime(2020),
      lastDate: DateTime(2100),
    );
    if (date != null) {
      setState(() {
        _selectedDate = date;
      });
    }
  }

  Future<void> _loadCourses() async {
    final auth = AuthScope.of(context);
    setState(() {
      _isLoading = true;
    });
    try {
      final data = await _api.get(
        auth.role == 'teacher' ? '/courses' : '/courses/enrolled',
        token: auth.token,
      ) as List<dynamic>;
      final courses = data
          .map((item) => Course.fromJson(item as Map<String, dynamic>))
          .toList();
      setState(() {
        _courses = courses;
        _selectedCourse = courses.isNotEmpty ? courses.first : null;
      });
      if (auth.role == 'teacher' && _selectedCourse != null) {
        await _loadStudents(_selectedCourse!.id);
      }
    } catch (error) {
      _showError(error);
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  Future<void> _loadStudents(String courseId) async {
    final auth = AuthScope.of(context);
    setState(() {
      _isLoading = true;
    });
    try {
      final data = await _api.get(
        '/courses/$courseId/students',
        token: auth.token,
      ) as List<dynamic>;
      final students = data
          .map((item) => Student.fromJson(item as Map<String, dynamic>))
          .toList();
      setState(() {
        _students = students;
        _presentStudentIds
          ..clear()
          ..addAll(students.map((student) => student.id));
      });
    } catch (error) {
      _showError(error);
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  Future<void> _markAttendance() async {
    final auth = AuthScope.of(context);
    final courseId = _selectedCourse?.id;
    if (courseId == null) {
      _showError('Select a course');
      return;
    }
    setState(() {
      _isSaving = true;
    });

    try {
      for (final student in _students) {
        await _api.post(
          '/attendance',
          token: auth.token,
          body: {
            'course_id': courseId,
            'date': _selectedDate.toIso8601String().split('T').first,
            'student_id': student.id,
            'present': _presentStudentIds.contains(student.id),
          },
        );
      }
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Attendance saved')),
        );
      }
    } catch (error) {
      _showError(error);
    } finally {
      if (mounted) {
        setState(() {
          _isSaving = false;
        });
      }
    }
  }

  Future<void> _loadAttendance() async {
    final auth = AuthScope.of(context);
    setState(() {
      _isLoading = true;
      _records = [];
    });
    try {
      final courseId = _selectedCourse?.id;
      final data = await _api.get(
        '/attendance',
        token: auth.token,
        query: {
          if (courseId != null) 'course_id': courseId,
        },
      ) as List<dynamic>;
      setState(() {
        _records = data
            .map((item) => AttendanceRecord.fromJson(item as Map<String, dynamic>))
            .toList();
      });
    } catch (error) {
      _showError(error);
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  Future<void> _loadSubjectPercentages() async {
    final auth = AuthScope.of(context);
    if (auth.userId == null) return;
    setState(() {
      _isLoading = true;
      _subjectAttendance = [];
    });
    try {
      final data = await _api.get(
        '/attendance/student/${auth.userId}/subjects',
        token: auth.token,
      ) as List<dynamic>;
      setState(() {
        _subjectAttendance = data
            .map((item) => SubjectAttendance.fromJson(item as Map<String, dynamic>))
            .toList();
      });
    } catch (error) {
      _showError(error);
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  void _showError(Object error) {
    if (!mounted) {
      return;
    }
    final message = error.toString().replaceFirst('Exception: ', '');
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final auth = AuthScope.of(context);
    final isTeacher = auth.role == 'teacher';

    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        Text(
          'Attendance',
          style: Theme.of(context).textTheme.headlineMedium,
        ),
        const SizedBox(height: 8),
        Text(isTeacher
            ? 'Mark daily attendance for enrolled students.'
            : 'Track your attendance history.'),
        const SizedBox(height: 20),
        Card(
          elevation: 0,
          color: Colors.white,
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                _buildCoursePicker(isTeacher),
                if (isTeacher) ...[
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Text(
                        'Date: ${_selectedDate.toIso8601String().split('T').first}',
                      ),
                      const SizedBox(width: 12),
                      TextButton(
                        onPressed: _pickDate,
                        child: const Text('Pick date'),
                      ),
                    ],
                  ),
                  SwitchListTile(
                    value: _presentStudentIds.length == _students.length &&
                        _students.isNotEmpty,
                    title: const Text('Mark all present'),
                    onChanged: (value) {
                      setState(() {
                        if (value) {
                          _presentStudentIds
                            ..clear()
                            ..addAll(_students.map((student) => student.id));
                        } else {
                          _presentStudentIds.clear();
                        }
                      });
                    },
                  ),
                  _buildStudentList(),
                  const SizedBox(height: 8),
                  SizedBox(
                    width: double.infinity,
                    child: FilledButton(
                      onPressed: _isSaving ? null : _markAttendance,
                      child: _isSaving
                          ? const SizedBox(
                              height: 18,
                              width: 18,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Text('Save attendance'),
                    ),
                  ),
                ] else ...[
                  const SizedBox(height: 12),
                  SizedBox(
                    width: double.infinity,
                    child: FilledButton(
                      onPressed: _isLoading ? null : _loadAttendance,
                      child: const Text('Load attendance'),
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
        if (!isTeacher) ...[
          const SizedBox(height: 20),
          Row(
            children: [
              Expanded(
                child: FilledButton(
                  onPressed: _isLoading ? null : _loadAttendance,
                  child: const Text('Load attendance'),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: FilledButton(
                  onPressed: _isLoading ? null : _loadSubjectPercentages,
                  child: const Text('My percentages'),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          if (_isLoading)
            const Center(child: CircularProgressIndicator())
          else if (_records.isEmpty)
            const Text('No records yet')
          else
            ..._records.map(
              (record) => Card(
                elevation: 0,
                color: Colors.white,
                child: ListTile(
                  title: Text(record.courseId),
                  subtitle: Text('Date: ${record.date}'),
                  trailing: Icon(
                    record.present ? Icons.check_circle : Icons.cancel,
                    color: record.present
                        ? const Color(0xFF0F766E)
                        : Colors.redAccent,
                  ),
                ),
              ),
            ),
          if (_subjectAttendance.isNotEmpty) ...[
            const SizedBox(height: 12),
            Text('Attendance Percentage', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            ..._subjectAttendance.map((s) => Card(
                  elevation: 0,
                  color: Colors.white,
                  child: ListTile(
                    title: Text(s.subjectCode),
                    subtitle: Text('Attended ${s.attendedClasses}/${s.totalClasses} classes'),
                    trailing: Text('${s.attendancePercentage.toStringAsFixed(1)}%'),
                  ),
                )),
          ],
        ],
      ],
    );
  }

  Widget _buildCoursePicker(bool isTeacher) {
    if (_courses.isEmpty) {
      return Text(
        isTeacher
            ? 'Create a course first to mark attendance.'
            : 'No enrolled courses yet.',
      );
    }

    return DropdownButtonFormField<String>(
      value: _selectedCourse?.id,
      decoration: const InputDecoration(labelText: 'Course'),
      items: _courses
          .map((course) => DropdownMenuItem(
                value: course.id,
                child: Text('${course.name} (${course.code})'),
              ))
          .toList(),
      onChanged: (value) async {
        final selected = _courses.firstWhere((course) => course.id == value);
        setState(() {
          _selectedCourse = selected;
        });
        if (isTeacher) {
          await _loadStudents(selected.id);
        } else {
          setState(() {
            _records = [];
          });
        }
      },
    );
  }

  Widget _buildStudentList() {
    if (_isLoading) {
      return const Padding(
        padding: EdgeInsets.only(top: 16),
        child: Center(child: CircularProgressIndicator()),
      );
    }
    if (_students.isEmpty) {
      return const Padding(
        padding: EdgeInsets.only(top: 16),
        child: Text('No enrolled students yet'),
      );
    }

    return Column(
      children: _students
          .map(
            (student) => CheckboxListTile(
              value: _presentStudentIds.contains(student.id),
              title: Text(student.email),
              subtitle: Text(student.id),
              onChanged: (value) {
                setState(() {
                  if (value == true) {
                    _presentStudentIds.add(student.id);
                  } else {
                    _presentStudentIds.remove(student.id);
                  }
                });
              },
            ),
          )
          .toList(),
    );
  }
}
