import 'package:flutter/material.dart';

void main() {
  runApp(const XAMApp());
}

class XAMApp extends StatelessWidget {
  const XAMApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(home: const HomeScreen());
  }
}

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(body: Center(child: Text("соси")));
  }
}
