import 'package:flutter/material.dart';

import 'core/auth_state.dart';
import 'screens/attendance_screen.dart';
import 'screens/courses_screen.dart';
import 'screens/login_screen.dart';
import 'screens/profile_screen.dart';

class AttendanceApp extends StatefulWidget {
  const AttendanceApp({super.key});

  @override
  State<AttendanceApp> createState() => _AttendanceAppState();
}

class _AttendanceAppState extends State<AttendanceApp> {
  late final AuthState _authState;

  @override
  void initState() {
    super.initState();
    _authState = AuthState();
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = ColorScheme.fromSeed(
      seedColor: const Color(0xFF0F766E),
      brightness: Brightness.light,
    );

    return AuthScope(
      authState: _authState,
      child: MaterialApp(
        debugShowCheckedModeBanner: false,
        title: 'Attendance',
        theme: ThemeData(
          colorScheme: colorScheme,
          textTheme: ThemeData.light().textTheme,
          scaffoldBackgroundColor: const Color(0xFFF6F7F9),
          useMaterial3: true,
        ),
        home: const AuthGate(),
      ),
    );
  }
}

class AuthGate extends StatelessWidget {
  const AuthGate({super.key});

  @override
  Widget build(BuildContext context) {
    final auth = AuthScope.of(context);

    return AnimatedBuilder(
      animation: auth,
      builder: (context, _) {
        return AnimatedSwitcher(
          duration: const Duration(milliseconds: 300),
          child: auth.isAuthenticated
              ? const HomeShell()
              : const LoginScreen(),
        );
      },
    );
  }
}

class HomeShell extends StatefulWidget {
  const HomeShell({super.key});

  @override
  State<HomeShell> createState() => _HomeShellState();
}

class _HomeShellState extends State<HomeShell> {
  int _index = 0;

  final List<Widget> _screens = const [
    CoursesScreen(),
    AttendanceScreen(),
    ProfileScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_index],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (index) {
          setState(() {
            _index = index;
          });
        },
        destinations: const [
          NavigationDestination(icon: Icon(Icons.menu_book), label: 'Courses'),
          NavigationDestination(icon: Icon(Icons.check_circle), label: 'Attendance'),
          NavigationDestination(icon: Icon(Icons.person), label: 'Profile'),
        ],
      ),
    );
  }
}
