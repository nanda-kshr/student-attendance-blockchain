import 'package:flutter/material.dart';

import '../core/api_client.dart';
import '../core/auth_state.dart';
import '../models/course.dart';

class CoursesScreen extends StatefulWidget {
  const CoursesScreen({super.key});

  @override
  State<CoursesScreen> createState() => _CoursesScreenState();
}

class _CoursesScreenState extends State<CoursesScreen> {
  final ApiClient _api = ApiClient();
  final _nameController = TextEditingController();
  final _codeController = TextEditingController();

  bool _didLoad = false;
  bool _isLoading = true;
  String? _error;
  List<Course> _courses = [];
  List<Course> _myCourses = [];
  final Set<String> _enrolledCourseIds = {};

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (!_didLoad) {
      _didLoad = true;
      _loadCourses();
    }
  }

  @override
  void dispose() {
    _nameController.dispose();
    _codeController.dispose();
    super.dispose();
  }

  Future<void> _loadCourses() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final auth = AuthScope.of(context);
      final data = await _api.get(
        '/courses',
        token: auth.token,
      ) as List<dynamic>;
      final courses = data
          .map((item) => Course.fromJson(item as Map<String, dynamic>))
          .toList();

      if (auth.role == 'student') {
        final enrolled = await _api.get(
          '/courses/enrolled',
          token: auth.token,
        ) as List<dynamic>;
        final myCourses = enrolled
            .map((item) => Course.fromJson(item as Map<String, dynamic>))
            .toList();
        _enrolledCourseIds
          ..clear()
          ..addAll(myCourses.map((course) => course.id));
        setState(() {
          _courses = courses;
          _myCourses = myCourses;
        });
      } else {
        _enrolledCourseIds.clear();
        setState(() {
          _courses = courses;
          _myCourses = [];
        });
      }
    } catch (error) {
      if (mounted) {
        setState(() {
          _error = error.toString().replaceFirst('Exception: ', '');
        });
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  Future<void> _createCourse() async {
    final auth = AuthScope.of(context);
    try {
      await _api.post(
        '/courses',
        token: auth.token,
        body: {
          'name': _nameController.text.trim(),
          'code': _codeController.text.trim(),
        },
      );
      _nameController.clear();
      _codeController.clear();
      await _loadCourses();
    } catch (error) {
      _showError(error);
    }
  }

  Future<void> _updateCourse(Course course) async {
    final auth = AuthScope.of(context);
    final nameController = TextEditingController(text: course.name);
    final codeController = TextEditingController(text: course.code);

    final result = await showDialog<bool>(
      context: context,
      builder: (_) {
        return AlertDialog(
          title: const Text('Update course'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: nameController,
                decoration: const InputDecoration(labelText: 'Name'),
              ),
              TextField(
                controller: codeController,
                decoration: const InputDecoration(labelText: 'Code'),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(false),
              child: const Text('Cancel'),
            ),
            FilledButton(
              onPressed: () => Navigator.of(context).pop(true),
              child: const Text('Save'),
            ),
          ],
        );
      },
    );

    if (result != true) {
      return;
    }

    try {
      await _api.put(
        '/courses/${course.id}',
        token: auth.token,
        body: {
          'name': nameController.text.trim(),
          'code': codeController.text.trim(),
        },
      );
      await _loadCourses();
    } catch (error) {
      _showError(error);
    }
  }

  Future<void> _deleteCourse(Course course) async {
    final auth = AuthScope.of(context);
    try {
      await _api.delete('/courses/${course.id}', token: auth.token);
      await _loadCourses();
    } catch (error) {
      _showError(error);
    }
  }

  Future<void> _enrollCourse(Course course) async {
    final auth = AuthScope.of(context);
    try {
      await _api.post('/courses/${course.id}/enroll', token: auth.token);
      _enrolledCourseIds.add(course.id);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Enrolled in course')),
        );
      }
    } catch (error) {
      _showError(error);
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

    return RefreshIndicator(
      onRefresh: _loadCourses,
      child: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text(
            'Courses',
            style: Theme.of(context).textTheme.headlineMedium,
          ),
          const SizedBox(height: 8),
          Text(
            isTeacher
                ? 'Create and manage your classes.'
                : 'Browse available courses and enroll.',
          ),
          const SizedBox(height: 20),
          if (isTeacher) _buildCreateCard(),
          if (_isLoading)
            const Center(child: CircularProgressIndicator())
          else if (_error != null)
            Text(_error!)
          else if (isTeacher)
            ..._courses.map((course) => _CourseTile(
                  course: course,
                  isTeacher: true,
                  isEnrolled: false,
                  onEdit: () => _updateCourse(course),
                  onDelete: () => _deleteCourse(course),
                  onEnroll: () => _enrollCourse(course),
                ))
          else ...[
            _SectionHeader(title: 'My courses'),
            if (_myCourses.isEmpty)
              const Text('No enrolled courses yet')
            else
              ..._myCourses.map((course) => _CourseTile(
                    course: course,
                    isTeacher: false,
                    isEnrolled: true,
                    onEdit: () => _updateCourse(course),
                    onDelete: () => _deleteCourse(course),
                    onEnroll: () => _enrollCourse(course),
                  )),
            const SizedBox(height: 16),
            _SectionHeader(title: 'All courses'),
            if (_courses.isEmpty)
              const Text('No courses available')
            else
              ..._courses.map((course) => _CourseTile(
                    course: course,
                    isTeacher: false,
                    isEnrolled: _enrolledCourseIds.contains(course.id),
                    onEdit: () => _updateCourse(course),
                    onDelete: () => _deleteCourse(course),
                    onEnroll: () => _enrollCourse(course),
                  )),
          ],
        ],
      ),
    );
  }

  Widget _buildCreateCard() {
    return Card(
      elevation: 0,
      color: Colors.white,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('New course',
                style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 12),
            TextField(
              controller: _nameController,
              decoration: const InputDecoration(labelText: 'Name'),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _codeController,
              decoration: const InputDecoration(labelText: 'Code'),
            ),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: FilledButton(
                onPressed: _createCourse,
                child: const Text('Create course'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _CourseTile extends StatelessWidget {
  const _CourseTile({
    required this.course,
    required this.isTeacher,
    required this.isEnrolled,
    required this.onEdit,
    required this.onDelete,
    required this.onEnroll,
  });

  final Course course;
  final bool isTeacher;
  final bool isEnrolled;
  final VoidCallback onEdit;
  final VoidCallback onDelete;
  final VoidCallback onEnroll;

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 0,
      color: Colors.white,
      child: ListTile(
        title: Text(course.name),
        subtitle: Text('Code: ${course.code}'),
        trailing: isTeacher
            ? Wrap(
                spacing: 8,
                children: [
                  IconButton(
                    icon: const Icon(Icons.edit),
                    onPressed: onEdit,
                  ),
                  IconButton(
                    icon: const Icon(Icons.delete_outline),
                    onPressed: onDelete,
                  ),
                ],
              )
            : FilledButton(
                onPressed: isEnrolled ? null : onEnroll,
                child: Text(isEnrolled ? 'Enrolled' : 'Enroll'),
              ),
      ),
    );
  }
}

class _SectionHeader extends StatelessWidget {
  const _SectionHeader({required this.title});

  final String title;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Text(
        title,
        style: Theme.of(context).textTheme.titleMedium,
      ),
    );
  }
}
