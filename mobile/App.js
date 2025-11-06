/**
 * AdultingOS Mobile App - Main Entry Point
 * React Native/Expo app for life admin assistant
 */
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet } from 'react-native';

// Import screens
import TasksScreen from './src/screens/TasksScreen';
import ChatScreen from './src/screens/ChatScreen';
import ProfileScreen from './src/screens/ProfileScreen';

const Tab = createBottomTabNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <StatusBar style="auto" />
      <Tab.Navigator
        screenOptions={{
          tabBarActiveTintColor: '#2563eb',
          tabBarInactiveTintColor: '#6b7280',
          headerStyle: {
            backgroundColor: '#f8fafc',
          },
          headerTintColor: '#1e293b',
        }}
      >
        <Tab.Screen 
          name="Tasks" 
          component={TasksScreen}
          options={{
            title: 'My Tasks',
            tabBarLabel: 'Tasks',
          }}
        />
        <Tab.Screen 
          name="Chat" 
          component={ChatScreen}
          options={{
            title: 'AI Assistant',
            tabBarLabel: 'Assistant',
          }}
        />
        <Tab.Screen 
          name="Profile" 
          component={ProfileScreen}
          options={{
            title: 'Profile',
            tabBarLabel: 'Profile',
          }}
        />
      </Tab.Navigator>
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
});